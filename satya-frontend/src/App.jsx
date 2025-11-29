import React, { useState } from 'react';
import { 
  ShieldCheck, Activity, Terminal, CheckCircle, AlertTriangle, 
  Search, LayoutDashboard, Database, Lock, Clock, Server,
  ChevronRight, ExternalLink
} from 'lucide-react';

const App = () => {
  const [inputClaim, setInputClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  // Live Session History
  const [history, setHistory] = useState([]); 

  const handleVerify = async () => {
    if (!inputClaim) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/verify_and_log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claim: inputClaim })
      });
      
      const data = await response.json();
      
      if (data.detail) {
        alert("Backend Error: " + data.detail);
        setLoading(false);
        return;
      }

      setResult(data);
      setHistory(prev => [data, ...prev]);

    } catch (error) {
      console.error("API Error:", error);
      alert("⚠️ Backend not connected!");
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden">
      
      {/* --- SIDEBAR --- */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex-col hidden md:flex">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-emerald-500/10 p-2 rounded-lg">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">SatyaChain</span>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {/* Active Console Button */}
          <div className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 transition-all cursor-default">
            <LayoutDashboard size={18} />
            <span className="font-medium text-sm">Verification Console</span>
            <ChevronRight size={14} className="ml-auto" />
          </div>

          {/* Functional Ledger Explorer Link */}
          <a 
            href="http://localhost:8000/chain" 
            target="_blank" 
            rel="noopener noreferrer"
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition-all group"
          >
            <Database size={18} className="group-hover:text-sky-400 transition-colors"/>
            <span className="font-medium text-sm">Ledger Explorer</span>
            <ExternalLink size={14} className="ml-auto opacity-0 group-hover:opacity-50 transition-opacity" />
          </a>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 text-xs">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-bold text-emerald-400">SYSTEM ONLINE</span>
            </div>
            <div className="flex justify-between text-slate-500">
              <span>Node Status</span>
              <span className="text-slate-300">Synced</span>
            </div>
          </div>
        </div>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="flex-1 flex flex-col relative">
        {/* Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between px-6">
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <span className="flex items-center gap-2"><Server size={14} /> Mainnet-Beta</span>
            <span className="w-px h-4 bg-slate-700"></span>
            <span className="flex items-center gap-2"><Lock size={14} /> Secured via Proof-of-Work</span>
          </div>
          <div className="text-xs font-mono text-slate-500">v2.0.5-stable</div>
        </header>

        {/* Dashboard Grid */}
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            
            {/* LEFT COLUMN (2/3 width) */}
            <div className="lg:col-span-2 flex flex-col gap-6 overflow-y-auto pr-2">
              
              {/* Search Box */}
              <div className="bg-slate-900 p-1 rounded-2xl border border-slate-700 shadow-2xl">
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Enter claim URL or text to verify..." 
                    className="flex-1 bg-transparent border-none text-white px-6 py-4 focus:ring-0 text-lg outline-none placeholder-slate-600 font-light"
                    value={inputClaim}
                    onChange={(e) => setInputClaim(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleVerify()}
                  />
                  <button 
                    onClick={handleVerify}
                    disabled={loading}
                    className="bg-slate-800 hover:bg-slate-700 text-emerald-400 px-8 font-medium transition-all rounded-xl m-1 border border-slate-700 disabled:opacity-50"
                  >
                    {loading ? <Activity className="animate-spin" /> : <Search />}
                  </button>
                </div>
              </div>

              {/* Loading State */}
              {loading && (
                <div className="flex-1 flex flex-col items-center justify-center bg-slate-900/50 rounded-2xl border border-slate-800 border-dashed animate-pulse min-h-[300px]">
                   <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                   <p className="text-slate-400 font-mono">Agentic AI is investigating sources...</p>
                </div>
              )}

              {/* Result Card */}
              {result && !loading && (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom-4">
                  <div className="p-6 border-b border-slate-800 flex justify-between items-start bg-slate-900/50">
                    <div className="flex gap-4">
                      <div className={`p-3 rounded-xl ${result.satya_score.trust_score > 70 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                        {result.satya_score.trust_score > 70 ? <CheckCircle size={28} /> : <AlertTriangle size={28} />}
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-white">{result.satya_score.verdict}</h2>
                        <p className="text-slate-400 text-sm">AI Confidence Score</p>
                      </div>
                    </div>
                    <div className={`text-5xl font-black ${result.satya_score.trust_score > 70 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {result.satya_score.trust_score}
                    </div>
                  </div>
                  
                  <div className="p-6 space-y-6">
                    <div>
                      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Agent Summary</h3>
                      <p className="text-lg text-slate-200 leading-relaxed">{result.satya_score.claim_summary}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                       <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                         <h4 className="text-xs font-bold text-slate-500 uppercase mb-3">Verified Sources</h4>
                         <ul className="space-y-2">
                           {result.satya_score.evidence.map((link, i) => (
                             <li key={i} className="flex items-center gap-2 text-xs text-sky-400 truncate">
                               <div className="w-1.5 h-1.5 rounded-full bg-sky-500"></div>
                               <a href={link} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                 {link}
                               </a>
                             </li>
                           ))}
                         </ul>
                       </div>
                       <div className="bg-black p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2 relative overflow-hidden">
                         <h4 className="text-emerald-500 font-bold uppercase flex items-center gap-2"><Terminal size={14}/> Immutable Ledger</h4>
                         <div className="flex justify-between text-slate-500"><span>Block Index</span> <span className="text-slate-300">#{result.blockchain_record.index}</span></div>
                         <div className="pt-2 border-t border-slate-800">
                           <div className="text-slate-500 mb-1">Transaction Hash</div>
                           <div className="text-slate-600 break-all">{result.blockchain_record.hash}</div>
                         </div>
                       </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN (1/3 width): Live Session Feed */}
            <div className="hidden lg:flex flex-col bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
              <div className="p-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <Activity size={18} className="text-emerald-400" /> Recent Blocks
                </h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {history.length === 0 ? (
                  <div className="text-center text-slate-600 py-20 italic px-4">
                    Verify a claim to mine the first block...
                  </div>
                ) : (
                  history.map((item, idx) => (
                    <div key={idx} className="p-3 bg-slate-950 rounded-lg border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group animate-in fade-in slide-in-from-right-4">
                      <div className="flex justify-between items-start mb-1">
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${item.satya_score.trust_score > 70 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                          {item.satya_score.verdict}
                        </span>
                        <span className="text-[10px] font-mono text-slate-500">#{item.blockchain_record.index}</span>
                      </div>
                      <p className="text-xs text-slate-300 line-clamp-2 mb-2 font-medium">{item.satya_score.claim_summary}</p>
                      <div className="flex items-center gap-1 text-[10px] text-slate-600 font-mono group-hover:text-emerald-500/50">
                        <Lock size={10} /> {item.blockchain_record.hash.substring(0, 16)}...
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
};

export default App;