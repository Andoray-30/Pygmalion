// 简单的 SVG 图标组件（无需外部库）
const IconSend = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>;
const IconSettings = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m2.12 2.12l4.24 4.24M1 12h6m6 0h6m-17.78-7.78l4.24-4.24m2.12-2.12l4.24-4.24"></path></svg>;
const IconPaperclip = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 0 19.8 4.3M22 12.5a10 10 0 0 0-19.8-4.2"></path></svg>;
const IconX = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>;
const IconCpu = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>;
const IconUser = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>;
const IconSparkles = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>;
const IconBot = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"></rect><line x1="9" y1="9" x2="9" y2="15"></line><line x1="15" y1="9" x2="15" y2="15"></line></svg>;
const IconActivity = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>;

const { useState, useEffect, useRef } = React;

// 头像组件
const Avatar = ({ role }) => {
  const styles = {
    user: "bg-slate-600",
    system: "bg-blue-600",
    artist: "bg-purple-600",
    critic: "bg-amber-600"
  };
  
  const icons = {
    user: <IconUser />,
    system: <IconCpu />,
    artist: <IconSparkles />,
    critic: <IconActivity />
  };

  return (
    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg text-white ${styles[role] || styles.system}`}>
      {icons[role] || icons.system}
    </div>
  );
};

// 消息气泡组件
const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <Avatar role={message.sender} />
      
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {message.senderName}
          </span>
          <span className="text-[10px] text-slate-600">
            {new Date(message.timestamp).toLocaleTimeString([], {hour12: false, hour:'2-digit', minute:'2-digit'})}
          </span>
        </div>

        <div className={`p-4 rounded-2xl shadow-md text-sm leading-relaxed ${
          isUser 
            ? 'bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-tr-none' 
            : 'bg-[#1e232b] border border-white/5 text-slate-200 rounded-tl-none'
        }`}>
          {message.content && <p className="whitespace-pre-wrap">{message.content}</p>}

          {message.type === 'image' && (
            <div className="mt-3 relative group rounded-xl overflow-hidden border border-white/10">
              <img src={message.imageUrl} alt="Generated" className="w-full max-w-md h-auto object-cover" onError={(e) => e.target.src = '/static/images/placeholder.png'} />
            </div>
          )}

          {message.scores && (
            <div className="mt-3 bg-black/20 p-3 rounded-lg border border-white/5 text-xs">
              <div className="flex justify-between items-center mb-2">
                <span className="text-slate-400">总体评分</span>
                <span className="text-amber-400 font-bold">{(message.scores.final_score || 0).toFixed(3)}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(message.scores || {}).map(([key, val]) => {
                    if (['final_score'].includes(key)) return null;
                    return <div key={key} className="flex justify-between"><span className="text-slate-500">{key}</span><span className="text-slate-300">{typeof val === 'number' ? val.toFixed(2) : val}</span></div>;
                })}
              </div>
            </div>
          )}

          {message.type === 'progress' && (
            <div className="mt-2 w-64">
              <div className="flex justify-between text-xs mb-1 text-purple-300">
                <span>处理中...</span>
                <span>{Math.floor(message.progress || 0)}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                  style={{ width: `${message.progress || 0}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 'init-1',
      sender: 'system',
      senderName: '系统核心',
      type: 'text',
      content: 'Pygmalion 引擎已启动，协作系统准备就绪。',
      timestamp: Date.now()
    }
  ]);
  
  const [input, setInput] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [refImage, setRefImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [serverRefImagePath, setServerRefImagePath] = useState(null);

  const [config, setConfig] = useState({
    targetScore: 0.85,
    maxIterations: 5,
    cfgScale: 7.0
  });

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Socket 连接
  useEffect(() => {
    try {
      const newSocket = io();

      newSocket.on('connect', () => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: 'system',
          senderName: '系统',
          content: '✓ 已连接到服务器',
          type: 'text',
          timestamp: Date.now()
        }]);
      });

      newSocket.on('message', (payload) => {
        const { type, data } = payload;
        
        if (type === 'status_update') {
          if (data.progress !== undefined) {
            setMessages(prev => {
              const lastMsg = prev[prev.length - 1];
              if (lastMsg?.type === 'progress') {
                const updated = [...prev];
                updated[prev.length - 1] = {...lastMsg, progress: data.progress, content: data.status};
                return updated;
              }
              return [...prev, {
                id: Date.now(),
                sender: 'system',
                senderName: '进度',
                type: 'progress',
                content: data.status || '处理中',
                progress: data.progress || 0,
                timestamp: Date.now()
              }];
            });
          }
        } else if (type === 'score_update') {
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender: 'critic',
            senderName: '评审员',
            content: `迭代 #${data.iteration} 完成\n评分: ${data.current_score.toFixed(3)}`,
            type: 'text',
            timestamp: Date.now(),
            scores: data.scores_detail
          }]);
        } else if (type === 'image_generated') {
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender: 'artist',
            senderName: '生成器',
            content: `迭代 #${data.iteration} 预览`,
            type: 'image',
            imageUrl: data.image_path,
            timestamp: Date.now()
          }]);
        } else if (type === 'completion') {
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender: 'system',
            senderName: '完成',
            content: `任务完成！总得分: ${data.best_score.toFixed(3)}`,
            type: 'text',
            timestamp: Date.now()
          }]);
        }
      });

      setSocket(newSocket);
      return () => newSocket.close();
    } catch(err) {
      console.error('Socket connection error:', err);
    }
  }, []);

  const handleSend = () => {
    if (!input.trim() && !serverRefImagePath) return;
    if (!socket?.connected) {
      alert('未连接到服务器');
      return;
    }

    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: 'user',
      senderName: '用户',
      content: input,
      type: 'text',
      timestamp: Date.now()
    }]);
    
    const payload = {
      theme: input,
      target_score: parseFloat(config.targetScore),
      max_iterations: parseInt(config.maxIterations),
      reference_image_path: serverRefImagePath
    };
    
    socket.emit('start_generation', payload);
    setInput("");
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setRefImage(URL.createObjectURL(file));
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload_reference', { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        setIsUploading(false);
        if (data.success) {
          setServerRefImagePath(data.path);
        } else {
          alert('上传失败');
          setRefImage(null);
        }
      })
      .catch(err => {
        setIsUploading(false);
        console.error(err);
      });
  };

  return (
    <div className="flex h-screen bg-[#0f1115] text-slate-200 overflow-hidden">
      
      <div className={`flex flex-col border-r border-white/5 bg-[#16191e] transition-all ${showSettings ? 'w-80' : 'w-0 overflow-hidden'}`}>
        <div className="p-4 border-b border-white/5 flex justify-between items-center">
          <h2 className="font-bold text-slate-300 flex items-center gap-2">
            <IconSettings className="w-4 h-4" /> 参数配置
          </h2>
          <button onClick={() => setShowSettings(false)} className="hover:text-white"><IconX className="w-4 h-4"/></button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <label className="text-xs font-bold text-slate-500">目标评分</label>
            <input type="range" min="0.5" max="0.99" step="0.01" value={config.targetScore} onChange={(e) => setConfig({...config, targetScore: e.target.value})} className="w-full" />
            <div className="text-right text-xs text-purple-400">{config.targetScore}</div>
          </div>
          <div>
            <label className="text-xs font-bold text-slate-500">最大迭代</label>
            <input type="range" min="1" max="20" value={config.maxIterations} onChange={(e) => setConfig({...config, maxIterations: e.target.value})} className="w-full" />
            <div className="text-right text-xs text-purple-400">{config.maxIterations}</div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#16191e]/80">
          <div className="flex items-center gap-3">
            <IconBot className="w-6 h-6 text-purple-500" />
            <div>
              <h1 className="font-bold">Pygmalion AI</h1>
              <div className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${socket?.connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-[10px] text-slate-500">{socket?.connected ? '在线' : '离线'}</span>
              </div>
            </div>
          </div>
          <button onClick={() => setShowSettings(!showSettings)} className={`p-2 rounded-lg ${showSettings ? 'bg-purple-500/20' : 'hover:bg-white/5'}`}>
            <IconSettings className="w-5 h-5" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
          <div className="max-w-4xl mx-auto">
            {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="p-4 bg-gradient-to-t from-[#0f1115]">
          <div className="max-w-4xl mx-auto bg-[#1e232b] rounded-2xl border border-white/10 p-3 flex flex-col gap-2">
            {refImage && (
              <div className="absolute -top-20 left-6 bg-[#1e232b] p-2 rounded-lg border border-white/10 flex items-center gap-2">
                <img src={refImage} className="w-12 h-12 rounded object-cover" alt="Ref" />
                <button onClick={() => { setRefImage(null); setServerRefImagePath(null); }} className="text-red-400 hover:text-red-300"><IconX className="w-3 h-3" /></button>
              </div>
            )}

            <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }}} placeholder="输入指令..." className="w-full bg-transparent border-none text-slate-200 p-2 max-h-24 outline-none resize-none placeholder:text-slate-600" />
            
            <div className="flex justify-between items-center px-1">
              <button onClick={() => fileInputRef.current?.click()} className="p-1 text-slate-500 hover:text-purple-400"><IconPaperclip className="w-4 h-4" /></button>
              <input type="file" ref={fileInputRef} onChange={handleImageUpload} accept="image/*" hidden />
              <button onClick={handleSend} disabled={(!input.trim() && !serverRefImagePath) || isUploading} className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 text-white rounded-lg text-xs font-bold flex items-center gap-1">
                发送 <IconSend className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

const { useState, useEffect, useRef } = React;

// --- 组件定义 ---

// 1. 头像组件
const Avatar = ({ role }) => {
  const styles = {
    user: "bg-slate-600",
    system: "bg-blue-600",
    artist: "bg-purple-600",
    critic: "bg-amber-600"
  };
  
  const icons = {
    user: <User className="w-5 h-5 text-white" />,
    system: <Cpu className="w-5 h-5 text-white" />,
    artist: <Sparkles className="w-5 h-5 text-white" />,
    critic: <Activity className="w-5 h-5 text-white" />
  };

  return (
    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg ${styles[role] || styles.system}`}>
      {icons[role] || icons.system}
    </div>
  );
};

// 2. 消息气泡组件
const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      <Avatar role={message.sender} />
      
      <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {message.senderName}
          </span>
          <span className="text-[10px] text-slate-600">
            {new Date(message.timestamp).toLocaleTimeString([], {hour12: false, hour:'2-digit', minute:'2-digit'})}
          </span>
        </div>

        <div className={`p-4 rounded-2xl shadow-md text-sm leading-relaxed ${
          isUser 
            ? 'bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-tr-none' 
            : 'bg-[#1e232b] border border-white/5 text-slate-200 rounded-tl-none'
        }`}>
          {/* 文本内容 */}
          {message.content && <p className="whitespace-pre-wrap">{message.content}</p>}

          {/* 图片内容 */}
          {message.type === 'image' && (
            <div className="mt-3 relative group rounded-xl overflow-hidden border border-white/10 bg-black/20">
              <img src={message.imageUrl} alt="Generated" className="w-full max-w-md h-auto object-cover" />
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-sm">
                <a href={message.imageUrl} download target="_blank" className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-full text-xs font-bold text-white backdrop-blur-md border border-white/20 transition-all flex items-center gap-2">
                   查看原图
                </a>
              </div>
            </div>
          )}
          
          {/* 评分结果 */}
          {message.scores && (
            <div className="mt-3 bg-black/20 p-3 rounded-lg border border-white/5 text-xs">
                 <div className="flex justify-between items-center mb-2">
                     <span className="text-slate-400">总体评分</span>
                     <span className="text-amber-400 font-bold text-sm">{(message.scores.final_score || message.score || 0).toFixed(3)}</span>
                 </div>
                 <div className="grid grid-cols-2 gap-2">
                     {Object.entries(message.scores).map(([key, val]) => {
                         if (['final_score', 'total_score'].includes(key)) return null;
                         return (
                             <div key={key} className="flex justify-between">
                                 <span className="text-slate-500 capitalize">{key.replace('_score', '')}</span>
                                 <span className="text-slate-300">{typeof val === 'number' ? val.toFixed(2) : val}</span>
                             </div>
                         )
                     })}
                 </div>
            </div>
          )}

          {/* 进度条内容 */}
          {message.type === 'progress' && (
            <div className="mt-2 w-64">
              <div className="flex justify-between text-xs mb-1 text-purple-300">
                <span>正在渲染...</span>
                <span>{Math.floor(message.progress)}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300 ease-out"
                  style={{ width: `${message.progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  // 消息流状态
  const [messages, setMessages] = useState([
    {
      id: 'init-1',
      sender: 'system',
      senderName: '系统核心',
      type: 'text',
      content: 'Pygmalion 引擎已启动。多智能体协作环境准备就绪。\n我是您的调度员，您可以直接告诉我想要生成什么，或者在右侧面板调整详细参数。',
      timestamp: Date.now()
    }
  ]);
  
  // 输入与参数状态
  const [input, setInput] = useState("");
  const [showSettings, setShowSettings] = useState(false); // 默认隐藏设置栏
  const [refImage, setRefImage] = useState(null);
  const [refImageFile, setRefImageFile] = useState(null);
  const [serverRefImagePath, setServerRefImagePath] = useState(null); // 上传到服务器后的路径
  const [isUploading, setIsUploading] = useState(false);

  // 参数配置 (The "Context" for the agents)
  const [config, setConfig] = useState({
    model: "SDXL-base-1.0",
    steps: 20,
    cfgScale: 7.0,
    negativePrompt: "",
    targetScore: 0.85,
    maxIterations: 5,
    modelsAvailable: []
  });

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 获取初始配置
  useEffect(() => {
     fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            if(data.system_info && data.system_info.judgeModels) {
                setConfig(prev => ({...prev, modelsAvailable: data.system_info.judgeModels}));
            }
        });
  }, []);

  // Socket 连接
  useEffect(() => {
    // 自动判断Socket地址
    const socketProto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${window.location.protocol}//${window.location.host}`;
    
    console.log("Connecting to:", socketUrl);
    
    // @ts-ignore
    const newSocket = io(socketUrl, {
        transports: ['websocket', 'polling']
    });

    const addMsg = (sender, senderName, content, type='text', extra={}) => {
      setMessages(prev => [...prev, {
        id: Date.now() + Math.random(),
        sender,
        senderName,
        content,
        type,
        timestamp: Date.now(),
        ...extra
      }]);
    };

    newSocket.on('connect', () => {
      console.log('Socket connected:', newSocket.id);
      addMsg('system', '系统核心', '服务器连接成功。通信链路稳定。');
    });
    
    newSocket.on('connect_error', (error) => {
        console.error('Connection Error:', error);
    });

    newSocket.on('disconnect', () => {
      addMsg('system', '系统核心', '与服务器的连接已断开。', 'text');
    });
    
    // 监听各类服务器消息
    newSocket.on('message', (payload) => {
        // payload: { type: '...', data: ... }
        const { type, data } = payload;
        
        // 1. 进度条
        if (type === 'status_update') {
             // 简单的状态更新通常只包含文字状态
             // 可以选择性显示，或者作为系统消息
             // 这里为了不刷屏，只在控制台打印，或者更新UI顶部的状态栏（如果设计了）
             // 或者如果带有 progress 字段，显示进度条
             if (data.progress !== undefined) {
                 setMessages(prev => {
                    const lastMsg = prev[prev.length - 1];
                    if (lastMsg && lastMsg.type === 'progress') {
                      const updated = [...prev];
                      updated[prev.length - 1] = {
                        ...lastMsg,
                        progress: data.progress,
                        content: data.status || lastMsg.content
                      };
                      return updated;
                    } else {
                      return [...prev, {
                        id: Date.now(),
                        sender: 'system',
                        senderName: '任务进度',
                        type: 'progress',
                        content: data.status || '处理中...',
                        progress: data.progress || 0,
                        timestamp: Date.now()
                      }];
                    }
                  });
             } else {
                 // 纯文本状态更新，如果很重要就发消息
                 // addMsg('system', '状态', data.status);
             }
        }
        
        // 2. 创意建议 (DeepSeek)
        else if (type === 'suggestion') {
            addMsg('system', '创意中枢 (DeepSeek)', data.suggestion);
        }
        
        // 3. 图片生成完成
        else if (type === 'image_generated') {
             // 迭代中间图
             addMsg('artist', '艺术家', `迭代 #${data.iteration} 生成预览`, 'image', { imageUrl: data.image_path });
        }
        
        // 4. 评分结果
        else if (type === 'evaluation') {
             // 单个模型的评分，比较啰嗦，可以选择合并显示或者简化显示
             // addMsg('critic', data.sender, data.message);
        }
        
        // 5. 详细分数更新
        else if (type === 'score_update') {
            // 包含分数详情的重要更
             addMsg('critic', '综合评审', 
                `迭代 #${data.iteration} 评估完成\n总分: ${data.current_score.toFixed(3)}${data.is_best ? ' 🏆 新高分!' : ''}`, 
                'text', 
                { scores: data.scores_detail || {}, score: data.current_score }
            );
        }
        
        // 6. 最终完成
        else if (type === 'completion') {
             addMsg('system', '调度员', 
                `任务已完成!\n总迭代: ${data.total_iterations} 次\n最终得分: ${data.best_score.toFixed(3)}\n最佳图片已锁定。`,
                'image',
                { imageUrl: data.best_image }
             );
        }
        
        // 7. 错误
        else if (type === 'error') {
            addMsg('system', '错误警报', data.message || '发生未知错误');
        }
    });

    setSocket(newSocket);
    return () => newSocket.close();
  }, [config.model]); 

  // 处理发送
  const handleSend = () => {
    if (!input.trim() && !serverRefImagePath) return;
    if (!socket?.connected) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'system',
        senderName: '系统',
        content: '错误：未连接到服务器。',
        type: 'text',
        timestamp: Date.now()
      }]);
      return;
    }

    // 1. 用户消息上屏
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      senderName: '我',
      content: input,
      type: 'text',
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    // 2. 调度员响应
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'system',
        senderName: '调度员',
        content: `收到指令。已将任务分发给 [核心引擎 v4]。\n目标分数: ${config.targetScore}, 最大迭代: ${config.maxIterations}`,
        type: 'text',
        timestamp: Date.now()
      }]);
    }, 200);

    // 3. 构建请求 payload
    const payload = {
      theme: input,
      target_score: parseFloat(config.targetScore),
      max_iterations: parseInt(config.maxIterations),
      // 可选参数
      reference_image_path: serverRefImagePath, 
      quick_mode: false // 暂未在UI暴露
    };
    
    socket.emit('start_generation', payload);
  };

  // 处理图片上传
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 预览
      setRefImage(URL.createObjectURL(file));
      setRefImageFile(file);
      setIsUploading(true);
      
      // 真正上传到服务器
      const formData = new FormData();
      formData.append('file', file);
      
      fetch('/api/upload_reference', {
          method: 'POST',
          body: formData
      })
      .then(res => res.json())
      .then(data => {
          setIsUploading(false);
          if (data.success) {
              setServerRefImagePath(data.path); // 保存服务器绝对路径
              console.log("Upload success, server path:", data.path);
          } else {
              alert('上传失败: ' + data.error);
              setRefImage(null);
          }
      })
      .catch(err => {
          setIsUploading(false);
          console.error(err);
          alert('上传出错');
      });
    }
  };

  return (
    <div className="flex h-screen bg-[#0f1115] text-slate-200 font-sans overflow-hidden">
      
      {/* 侧边栏：参数配置 */}
      <div className={`flex flex-col border-r border-white/5 bg-[#16191e] transition-all duration-300 ease-in-out ${showSettings ? 'w-80' : 'w-0 opacity-0 overflow-hidden'}`}>
        <div className="p-5 border-b border-white/5 flex justify-between items-center">
          <h2 className="font-bold text-slate-300 flex items-center gap-2">
            <Settings className="w-4 h-4" /> 全局参数
          </h2>
          <button onClick={() => setShowSettings(false)} className="hover:text-white"><X className="w-4 h-4"/></button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          <div className="space-y-3">
             <label className="text-xs font-bold text-slate-500 uppercase">生成目标</label>
             <div className="space-y-4">
                 <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">目标评分</span>
                      <span className="text-purple-400 font-mono">{config.targetScore}</span>
                    </div>
                    <input 
                      type="range" min="0.5" max="0.99" step="0.01"
                      value={config.targetScore}
                      onChange={(e) => setConfig({...config, targetScore: e.target.value})}
                      className="w-full h-1.5 bg-[#0a0c10] rounded-full appearance-none cursor-pointer accent-purple-500" 
                    />
                 </div>
                 
                 <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">最大迭代次数</span>
                      <span className="text-purple-400 font-mono">{config.maxIterations}</span>
                    </div>
                    <input 
                      type="range" min="1" max="20" step="1"
                      value={config.maxIterations}
                      onChange={(e) => setConfig({...config, maxIterations: e.target.value})}
                      className="w-full h-1.5 bg-[#0a0c10] rounded-full appearance-none cursor-pointer accent-purple-500" 
                    />
                 </div>
             </div>
          </div>

          <div className="space-y-3">
             <label className="text-xs font-bold text-slate-500 uppercase">基础模型设定</label>
             <p className="text-[10px] text-slate-600">
                当前系统自动托管模型选择，但在微调阶段会尝试使用以下参数基准。
             </p>
             <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">初始 CFG</span>
                  <span className="text-purple-400 font-mono">{config.cfgScale}</span>
                </div>
                <input 
                  type="range" min="1" max="20" step="0.5"
                  value={config.cfgScale}
                  onChange={(e) => setConfig({...config, cfgScale: e.target.value})}
                  className="w-full h-1.5 bg-[#0a0c10] rounded-full appearance-none cursor-pointer accent-purple-500" 
                />
             </div>
          </div>
        </div>
      </div>

      {/* 主对话区域 */}
      <div className="flex-1 flex flex-col relative bg-[#0f1115]">
        {/* 顶部标题栏 */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#16191e]/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <Bot className="w-6 h-6 text-purple-500" />
            <div>
              <h1 className="font-bold text-slate-200">Pygmalion 协作组</h1>
              <div className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${socket?.connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-[10px] text-slate-500 uppercase font-medium">
                  {socket?.connected ? '在线 - 核心引擎就绪' : '离线 - 正在重连'}
                </span>
              </div>
            </div>
          </div>
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-purple-500/20 text-purple-400' : 'hover:bg-white/5 text-slate-400'}`}
          >
            <Settings className="w-5 h-5" />
          </button>
        </header>

        {/* 消息流 */}
        <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
          <div className="max-w-4xl mx-auto">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* 底部输入栏 */}
        <div className="p-6 pt-0 bg-gradient-to-t from-[#0f1115] to-transparent">
          <div className="max-w-4xl mx-auto bg-[#1e232b] rounded-2xl border border-white/10 shadow-2xl p-2 flex flex-col gap-2 relative">
            
            {/* 参考图预览气泡 */}
            {refImage && (
              <div className="absolute -top-24 left-0 bg-[#1e232b] p-2 rounded-xl border border-white/10 shadow-lg flex items-start gap-2">
                <img src={refImage} className={`w-16 h-16 rounded-lg object-cover ${isUploading ? 'opacity-50' : ''}`} alt="Ref" />
                {isUploading && <span className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] text-white font-bold">上传中</span>}
                <button 
                  onClick={() => { setRefImage(null); setServerRefImagePath(null); }}
                  className="bg-red-500/20 text-red-400 p-1 rounded-full hover:bg-red-500 hover:text-white transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}

            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="输入您的创意指令... (Shift+Enter 换行)"
              className="w-full bg-transparent border-none text-slate-200 p-3 max-h-32 focus:ring-0 outline-none resize-none placeholder:text-slate-600"
            />
            
            <div className="flex justify-between items-center px-2 pb-1">
              <div className="flex gap-2">
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-slate-500 hover:text-purple-400 hover:bg-purple-500/10 rounded-lg transition-colors"
                  title="上传参考图"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleImageUpload} 
                  accept="image/*" 
                  hidden 
                />
              </div>
              
              <button 
                onClick={handleSend}
                disabled={(!input.trim() && !serverRefImagePath) || isUploading}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                  (!input.trim() && !serverRefImagePath) || isUploading
                    ? 'bg-white/5 text-slate-600 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-900/40'
                }`}
              >
                发送指令 <Send className="w-3 h-3" />
              </button>
            </div>
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-600">
              Pygmalion Engine v4 • 深度协作生成系统
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// 渲染
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);