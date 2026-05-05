import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './components/Dashboard';
import { GitPullRequest, Search } from 'lucide-react';

const queryClient = new QueryClient();

function App() {
  const [prId, setPrId] = useState<string>('');
  const [activePr, setActivePr] = useState<string | null>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (prId) setActivePr(prId);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background font-sans antialiased">
        {!activePr ? (
          <div className="flex flex-col items-center justify-center min-h-screen px-4">
            <div className="w-full max-w-md space-y-8 text-center">
              <div className="flex justify-center">
                <div className="p-4 rounded-2xl bg-primary/10 text-primary">
                  <GitPullRequest className="w-12 h-12" />
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-extrabold tracking-tight">ContextDiff</h1>
                <p className="mt-2 text-muted-foreground">
                  Intelligent AI code review agent. Enter a PR ID to see the analysis.
                </p>
              </div>
              <form onSubmit={handleSearch} className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Enter PR ID (e.g., 123)"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border bg-background focus:ring-2 focus:ring-primary outline-none transition-all"
                    value={prId}
                    onChange={(e) => setPrId(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-bold hover:opacity-90 transition-opacity"
                >
                  Analyze
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div>
            <nav className="border-b bg-card px-6 py-3 flex justify-between items-center">
              <div className="flex items-center gap-2 font-bold text-xl cursor-pointer" onClick={() => setActivePr(null)}>
                <GitPullRequest className="w-6 h-6 text-primary" />
                <span>ContextDiff</span>
              </div>
              <button 
                onClick={() => setActivePr(null)}
                className="text-sm font-medium text-muted-foreground hover:text-foreground"
              >
                Switch PR
              </button>
            </nav>
            <Dashboard prId={activePr} />
          </div>
        )}
      </div>
    </QueryClientProvider>
  );
}

export default App;
