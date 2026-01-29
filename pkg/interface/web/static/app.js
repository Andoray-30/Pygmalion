/**
 * Pygmalion AI - 前端应用逻辑
 * 实时对话式的 AI 图片生成展示
 */

class PygmalionApp {
    constructor() {
        this.socket = null;  // 改为 socket（Socket.IO）
        this.isGenerating = false;
        this.sessionId = null;
        this.bestScore = 0;
        this.currentIter = 0;
        this.totalIters = 0;
        this.images = [];
        
        this.initElements();
        this.attachEventListeners();
        this.updateSliders();
        this.initSocketIO();  // 初始化 Socket.IO
    }

    initElements() {
        this.elements = {
            // 输入控制 (左侧面板)
            targetScore: document.getElementById('target-score'),
            scoreDisplay: document.getElementById('score-display'),
            maxIter: document.getElementById('max-iter'),
            iterDisplay: document.getElementById('iter-display'),
            quickMode: document.getElementById('quick-mode'),
            startBtn: document.getElementById('start-btn'),
            
            // 对话区域
            chatMessages: document.getElementById('chat-messages'),
            customInput: document.getElementById('custom-input'),
            sendBtn: document.getElementById('send-btn'),
            sessionId: document.getElementById('session-id'),
            
            // 结果面板
            status: document.getElementById('status'),
            bestScore: document.getElementById('best-score'),
            currentIter: document.getElementById('current-iter'),
            progressBar: document.getElementById('progress-bar'),
            progressText: null,
            bestImageWrapper: document.getElementById('best-image-wrapper'),
            thumbnailsContainer: document.getElementById('thumbnails-container'),
            
            // 设置模态框
            settingsModal: document.getElementById('settings-modal'),
            navSettings: document.getElementById('nav-settings'),
            closeSettings: document.querySelector('.close-btn'),
            cancelSettings: document.getElementById('cancel-settings'),
            saveSettings: document.getElementById('save-settings'),
            
            // 设置输入项
            msName: document.getElementById('ms-name'),
            msKey: document.getElementById('ms-key'),
            msUrl: document.getElementById('ms-url'),
            msModel: document.getElementById('ms-model'),
            
            sfName: document.getElementById('sf-name'),
            sfKey: document.getElementById('sf-key'),
            sfUrl: document.getElementById('sf-url'),
            sfModel: document.getElementById('sf-model')
        };
        
        // 确保 UI 元素存在后再操作
        if (this.elements.progressBar) {
            const progressContainer = this.elements.progressBar.parentElement;
            this.elements.progressText = document.createElement('div');
            this.elements.progressText.id = 'progress-text';
            this.elements.progressText.style.marginTop = '8px';
            this.elements.progressText.style.fontSize = '12px';
            this.elements.progressText.style.color = '#888';
            this.elements.progressText.style.textAlign = 'center';
            progressContainer.appendChild(this.elements.progressText);
        }
    }

    attachEventListeners() {
        this.elements.targetScore.addEventListener('input', (e) => {
            this.elements.scoreDisplay.textContent = e.target.value;
        });

        this.elements.maxIter.addEventListener('input', (e) => {
            this.elements.iterDisplay.textContent = e.target.value;
        });

        if (this.elements.startBtn) {
            this.elements.startBtn.addEventListener('click', () => this.startGeneration());
        }

        this.elements.sendBtn.addEventListener('click', () => this.handleChatInput());
        
        this.elements.customInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleChatInput();
            }
        });

        // 设置模态框事件
        if (this.elements.navSettings) {
            this.elements.navSettings.addEventListener('click', (e) => {
                e.preventDefault();
                this.openSettings();
            });
        }

        if (this.elements.closeSettings) {
            this.elements.closeSettings.addEventListener('click', () => this.closeSettings());
        }

        if (this.elements.cancelSettings) {
            this.elements.cancelSettings.addEventListener('click', () => this.closeSettings());
        }

        if (this.elements.saveSettings) {
            this.elements.saveSettings.addEventListener('click', () => this.handleSaveSettings());
        }

        // 点击模态框背景关闭
        window.addEventListener('click', (e) => {
            if (e.target === this.elements.settingsModal) {
                this.closeSettings();
            }
        });
    }

    updateSliders() {
        // 初始化滑块
        const updateSlider = (slider) => {
            const percentage = (slider.value - slider.min) / (slider.max - slider.min);
            slider.style.setProperty('--value', percentage);
        };

        this.elements.targetScore.addEventListener('input', function() {
            updateSlider(this);
        });

        this.elements.maxIter.addEventListener('input', function() {
            updateSlider(this);
        });
    }

    initSocketIO() {
        // 初始化 Socket.IO 连接
        if (typeof io === 'undefined') {
            console.error('Socket.IO 未加载');
            this.addMessage('系统', '❌ Socket.IO 库未加载，请刷新页面', 'error');
            return;
        }

        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ Socket.IO 已连接');
            this.addMessage('系统', '✅ 已连接到服务器', 'system');
        });
        
        this.socket.on('disconnect', () => {
            console.log('⚠️ Socket.IO 已断开');
            if (this.isGenerating) {
                this.addMessage('系统', '⚠️ 连接已断开', 'error');
                this.resetGeneration();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('连接错误:', error);
            this.addMessage('系统', '❌ 连接错误，请刷新页面重试', 'error');
        });
        
        // 监听服务器事件
        this.socket.on('session_created', (data) => {
            this.sessionId = data.session_id;
            this.elements.sessionId.textContent = `会话: ${this.sessionId}`;
            this.addMessage('系统', data.message, 'system');
        });
        
        // 所有事件现在统一通过 message 事件处理
        // 以确保数据格式统一并简化逻辑
        
        // 通用消息监听（用于接收所有类型的更新）
        this.socket.on('message', (data) => {
            const { type, data: msgData } = data;
            console.log('📨 收到消息:', type, msgData);
            
            // 根据消息类型处理
            switch(type) {
                case 'status_update':
                    this.elements.status.textContent = msgData.status;
                    break;
                case 'suggestion':
                    this.addMessage(msgData.sender || 'Deepseek 💡', msgData.message, 'deepseek');
                    break;
                case 'iteration_start':
                    this.currentIter = msgData.iteration;
                    this.totalIters = msgData.total;
                    this.elements.currentIter.textContent = `${msgData.iteration}/${msgData.total}`;
                    this.updateProgressBar();
                    this.addMessage('生成器', `🎨 开始第 ${msgData.iteration} 次迭代...`, 'generator');
                    break;
                case 'image_generated':
                    this.addMessage('生成器', `✅ 第 ${msgData.iteration} 张图片已生成`, 'generator');
                    if (msgData.image_path) {
                        this.addImageToGallery(msgData.image_path, msgData.iteration);
                    }
                    break;
                case 'evaluation':
                    this.addMessage(msgData.sender || '评分模型', msgData.message, 'evaluator');
                    break;
                case 'score_update':
                    this.handleScoreUpdate(msgData);
                    break;
                case 'completion':
                    this.addMessage('系统', 
                        `✅ 生成完成！\n最优分数: ${msgData.best_score.toFixed(3)}\n总迭代: ${msgData.total_iterations}\n总图片: ${msgData.total_images}`,
                        'system');
                    this.resetGeneration();
                    break;
                case 'error':
                    this.addMessage('系统', `❌ 错误: ${msgData.message}`, 'error');
                    this.resetGeneration();
                    break;
            }
        });
    }

    handleChatInput() {
        const text = this.elements.customInput.value.trim();
        if (!text) return;

        if (this.isGenerating) {
            // 如果正在生成，作为反馈发送
            this.sendCustomMessage(text);
        } else {
            // 如果未在生成，作为主题启动
            this.startGeneration(text);
        }
        
        this.elements.customInput.value = '';
    }

    startGeneration(theme = null) {
        if (this.isGenerating) {
            return;
        }

        const params = {
            theme: theme || (this.elements.theme ? this.elements.theme.value.trim() : 'enchanted forest'),
            target_score: parseFloat(this.elements.targetScore.value),
            max_iterations: parseInt(this.elements.maxIter.value),
            quick_mode: this.elements.quickMode.checked
        };

        if (!params.theme) {
            this.addMessage('系统', '⚠️ 请输入生成主题（如：猫娘、赛博朋克城市）', 'error');
            return;
        }
        
        if (!this.socket || !this.socket.connected) {
            this.addMessage('系统', '❌ 未连接到服务器，请刷新页面', 'error');
            return;
        }

        this.isGenerating = true;
        if (this.elements.startBtn) {
            this.elements.startBtn.disabled = true;
            this.elements.startBtn.textContent = '⏳ 生成中...';
        }
        
        // 清空消息区域和图片
        this.elements.chatMessages.innerHTML = '';
        this.elements.thumbnailsContainer.innerHTML = '';
        this.images = [];
        this.bestScore = 0;
        this.currentIter = 0;
        
        // 添加用户消息
        this.addMessage('你', params.theme, 'user');
        
        // 添加开始消息（带加载动画）
        this.addMessage('系统', '🚀 正在启动生成过程，请稍候...', 'system', null, true);
        
        // 发送生成请求
        this.socket.emit('start_generation', params);
    }

    sendCustomMessage(message) {
        this.addMessage('你', message, 'user');

        // 发送到后端作为反馈或新指令
        if (this.socket && this.socket.connected) {
            this.socket.emit('custom_message', { 
                content: message,
                session_id: this.sessionId
            });
            this.addMessage('系统', '📨 已收到您的新需求，正在尝试调整...', 'system', null, true);
        }
    }

    addMessage(sender, message, type = 'user', model = null, isLoading = false) {
        // 如果有正在加载的消息，先移除其加载状态
        const existingLoaders = this.elements.chatMessages.querySelectorAll('.status-loading');
        existingLoaders.forEach(el => el.remove());

        const messageEl = document.createElement('div');
        messageEl.className = `message ${type === 'user' ? 'user' : 'ai'}`;

        const avatar = this.getAvatarForType(type);
        const avatarEl = document.createElement('div');
        avatarEl.className = 'message-avatar';
        avatarEl.textContent = avatar;

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'message-bubble';

        const typeLabel = this.getTypeLabel(type);
        bubbleEl.innerHTML = `
            <div class="message-type">${sender}${model ? ` (${model})` : ''}</div>
            <div class="message-content">${this.escapeHtml(message)}</div>
            ${isLoading ? '<div class="status-loading"><span class="spinner"></span> AI 正在思考中...</div>' : ''}
        `;

        if (type === 'user') {
            messageEl.appendChild(bubbleEl);
            messageEl.appendChild(avatarEl);
        } else {
            messageEl.appendChild(avatarEl);
            messageEl.appendChild(bubbleEl);
        }

        this.elements.chatMessages.appendChild(messageEl);
        
        // 自动滚动到底部
        this.elements.chatMessages.scrollTo({
            top: this.elements.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    handleScoreUpdate(data) {
        // 更新迭代计数
        if (data.iteration !== undefined) {
            this.currentIter = data.iteration;
        }
        
        // 更新最高分数
        if (data.current_score !== undefined && data.current_score > this.bestScore) {
            this.bestScore = data.current_score;
            if (this.elements.bestScore) {
                this.elements.bestScore.textContent = data.current_score.toFixed(3);
            }
            this.addMessage('评分模型', 
                `🎯 新最优分数: ${data.current_score.toFixed(3)}`, 'evaluator');
        }
        
        // 更新进度条
        if (data.iteration !== undefined && data.max_iterations !== undefined) {
            const progress = (data.iteration / data.max_iterations) * 100;
            if (this.elements.progressBar) {
                this.elements.progressBar.style.width = progress + '%';
            }
            if (this.elements.progressText) {
                this.elements.progressText.textContent = 
                    `迭代: ${data.iteration}/${data.max_iterations} | 最优分数: ${this.bestScore.toFixed(3)}`;
            }
        }
        
        // 更新图片信息
        if (data.image_path !== undefined) {
            // 记录到本地数组
            this.images.push({
                score: data.current_score,
                path: data.image_path,
                iteration: data.iteration
            });

            this.addImageToGallery(data.image_path, data.current_score);
            // 默认更新最优图片区域
            if (data.is_best) {
                this.updateBestImage(data.image_path);
            }
        }
    }

    addImageToGallery(imagePath, score = null) {
        const thumbnail = document.createElement('div');
        thumbnail.className = 'image-thumbnail';
        thumbnail.style.position = 'relative';
        thumbnail.style.cursor = 'pointer';
        thumbnail.style.width = '100px';
        thumbnail.style.height = '100px';
        thumbnail.style.borderRadius = '8px';
        thumbnail.style.overflow = 'hidden';
        thumbnail.style.backgroundColor = '#eee';
        
        const img = document.createElement('img');
        img.src = imagePath;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.onload = () => {
            thumbnail.style.opacity = '1';
        };
        img.onerror = () => {
            console.error('图片加载失败:', imagePath);
            thumbnail.remove();
        };
        
        // 添加分数标签
        if (score !== null) {
            const scoreLabel = document.createElement('div');
            scoreLabel.className = 'score-label';
            scoreLabel.textContent = `⭐ ${score.toFixed(3)}`;
            scoreLabel.style.position = 'absolute';
            scoreLabel.style.bottom = '2px';
            scoreLabel.style.right = '2px';
            scoreLabel.style.background = 'rgba(0,0,0,0.7)';
            scoreLabel.style.color = '#fff';
            scoreLabel.style.padding = '2px 4px';
            scoreLabel.style.borderRadius = '3px';
            scoreLabel.style.fontSize = '10px';
            scoreLabel.style.zIndex = '10';
            thumbnail.appendChild(scoreLabel);
        }
        
        // 点击查看全图
        thumbnail.addEventListener('click', () => {
            this.updateBestImage(imagePath);
        });
        
        thumbnail.appendChild(img);
        if (this.elements.thumbnailsContainer) {
            this.elements.thumbnailsContainer.appendChild(thumbnail);
        }
        this.images.push({ path: imagePath, score });
    }

    addImageMessage(sender, imagePath, caption, type = 'ai', model = null) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type === 'user' ? 'user' : 'ai'}`;

        const avatar = this.getAvatarForType(type);
        const avatarEl = document.createElement('div');
        avatarEl.className = 'message-avatar';
        avatarEl.textContent = avatar;

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'message-bubble';

        bubbleEl.innerHTML = `
            <div class="message-type">${sender}${model ? ` (${model})` : ''}</div>
            <div class="message-content">${this.escapeHtml(caption)}</div>
            <img src="${imagePath}" alt="Generated Image" class="message-image">
        `;

        if (type === 'user') {
            messageEl.appendChild(bubbleEl);
            messageEl.appendChild(avatarEl);
        } else {
            messageEl.appendChild(avatarEl);
            messageEl.appendChild(bubbleEl);
        }

        messageEl.addEventListener('click', () => this.previewImage(imagePath));
        this.elements.chatMessages.appendChild(messageEl);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    updateBestImage(imagePath) {
        this.elements.bestImageWrapper.innerHTML = `
            <img src="${imagePath}" alt="Best Result" style="width: 100%; height: 100%; object-fit: cover;">
        `;
    }

    updateThumbnails() {
        this.elements.thumbnailsContainer.innerHTML = this.images
            .sort((a, b) => b.score - a.score)
            .slice(0, 9)
            .map((img, idx) => {
                const isBest = img.score === this.bestScore;
                return `
                    <div class="thumbnail ${isBest ? 'best' : ''}" 
                         onclick="app.previewImage('${img.path}'); return false;">
                        <img src="${img.path}" alt="Thumbnail ${idx + 1}">
                    </div>
                `;
            })
            .join('');
    }

    updateProgressBar() {
        const percentage = (this.currentIter / this.totalIters) * 100;
        this.elements.progressBar.style.width = `${percentage}%`;
    }

    sendCustomMessage() {
        const message = this.elements.customInput.value.trim();
        if (!message || !this.isGenerating) return;

        this.addMessage('你', message, 'user');
        this.elements.customInput.value = '';

        // 发送到后端
        if (this.socket && this.socket.connected) {
            this.socket.emit('custom_message', { content: message });
        }
    }

    resetGeneration() {
        this.isGenerating = false;
        this.elements.startBtn.disabled = false;
        this.elements.startBtn.textContent = '🚀 开始生成';
        // Socket.IO 连接保持，不需要关闭
    }

    previewImage(imagePath) {
        // 可选：实现图片预览弹窗
        console.log('预览:', imagePath);
    }

    getAvatarForType(type) {
        const avatars = {
            'user': '👤',
            'deepseek': '🧠',
            'generator': '🎨',
            'evaluator': '📊',
            'system': '⚙️',
            'error': '❌'
        };
        return avatars[type] || '💬';
    }

    getTypeLabel(type) {
        const labels = {
            'user': '你',
            'deepseek': 'Deepseek',
            'generator': '生成器',
            'evaluator': '评分模型',
            'system': '系统',
            'error': '错误'
        };
        return labels[type] || '未知';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================================
    // 设置管理逻辑
    // ============================================================

    async openSettings() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.style.display = 'block';
            await this.loadSettings();
        }
    }

    closeSettings() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.style.display = 'none';
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            // 填充 A 源
            if (this.elements.msName) this.elements.msName.value = data.EVAL_A_NAME || '';
            if (this.elements.msKey) this.elements.msKey.value = data.EVAL_A_KEY || '';
            if (this.elements.msUrl) this.elements.msUrl.value = data.EVAL_A_URL || '';
            if (this.elements.msModel) this.elements.msModel.value = data.EVAL_A_MODEL || '';
            
            // 填充 B 源
            if (this.elements.sfName) this.elements.sfName.value = data.EVAL_B_NAME || '';
            if (this.elements.sfKey) this.elements.sfKey.value = data.EVAL_B_KEY || '';
            if (this.elements.sfUrl) this.elements.sfUrl.value = data.EVAL_B_URL || '';
            if (this.elements.sfModel) this.elements.sfModel.value = data.EVAL_B_MODEL || '';
            
        } catch (error) {
            console.error('加载设置失败:', error);
            this.addMessage('系统', '❌ 无法从服务器加载 API 设置', 'error');
        }
    }

    async handleSaveSettings() {
        const data = {
            EVAL_A_NAME: this.elements.msName.value.trim(),
            EVAL_A_KEY: this.elements.msKey.value.trim(),
            EVAL_A_URL: this.elements.msUrl.value.trim(),
            EVAL_A_MODEL: this.elements.msModel.value.trim(),
            
            EVAL_B_NAME: this.elements.sfName.value.trim(),
            EVAL_B_KEY: this.elements.sfKey.value.trim(),
            EVAL_B_URL: this.elements.sfUrl.value.trim(),
            EVAL_B_MODEL: this.elements.sfModel.value.trim()
        };

        try {
            this.elements.saveSettings.disabled = true;
            this.elements.saveSettings.textContent = '⌛ 正在保存...';

            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                this.addMessage('系统', '✅ API 设置已成功保存并立即生效', 'system');
                this.closeSettings();
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('保存设置失败:', error);
            this.addMessage('系统', `❌ 保存设置失败: ${error.message}`, 'error');
        } finally {
            this.elements.saveSettings.disabled = false;
            this.elements.saveSettings.textContent = '保存并应用';
        }
    }
}

// 初始化应用
let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new PygmalionApp();
    console.log('✅ Pygmalion AI 应用已初始化');
});
