import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Badge } from './ui/Badge';
import { Shield, FileCode, Search, MessageSquare, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface Finding {
  severity: string;
  confidence: number;
  category: string;
  file: string;
  line: number;
  message: string;
  fix?: string;
}

interface AgentStep {
  agent: string;
  reasoning: string;
}

interface Report {
  overall_score: number;
  risk_level: string;
  findings: Finding[];
  agent_chain: AgentStep[];
}

export default function Dashboard({ prId }: { prId: string }) {
  const { data: report, isLoading, error } = useQuery<Report>({
    queryKey: ['review', prId],
    queryFn: async () => {
      const resp = await fetch(`http://localhost:8000/api/reviews/${prId}`);
      if (!resp.ok) throw new Error('Failed to fetch report');
      return resp.json();
    },
    refetchInterval: 5000, // Poll every 5s during hackathon demo
  });

  if (isLoading) return <div className="p-10 text-center">Analyzing Pull Request...</div>;
  if (error) return <div className="p-10 text-center text-red-500">Error: {(error as Error).message}</div>;
  if (!report || (report as any).status === 'not_found') {
    return <div className="p-10 text-center">Waiting for PR analysis to start...</div>;
  }

  const getSeverityVariant = (severity: string) => {
    const s = severity.toLowerCase();
    if (s === 'critical') return 'critical';
    if (s === 'high') return 'high';
    if (s === 'medium') return 'medium';
    return 'low';
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-center border-b pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ContextDiff Analysis</h1>
          <p className="text-muted-foreground">Pull Request #{prId}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Health Score</p>
            <p className={`text-4xl font-black ${report.overall_score > 70 ? 'text-green-500' : report.overall_score > 40 ? 'text-yellow-500' : 'text-red-500'}`}>
              {report.overall_score}/100
            </p>
          </div>
          <Badge variant={getSeverityVariant(report.risk_level)} className="text-lg px-4 py-1">
            {report.risk_level} Risk
          </Badge>
        </div>
      </header>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Agent Reasoning Chain */}
        <Card className="md:col-span-1 border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5 text-primary" />
              Agent Reasoning
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {report.agent_chain?.map((step, i) => (
                <div key={i} className="relative pl-6 border-l-2 border-primary/30 last:border-0">
                  <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-primary border-4 border-background" />
                  <h4 className="font-bold text-sm text-primary uppercase">{step.agent}</h4>
                  <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{step.reasoning}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Findings Table */}
        <Card className="md:col-span-2 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-destructive" />
              Security & Logic Findings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground font-medium">
                    <th className="text-left pb-3 px-2">Severity</th>
                    <th className="text-left pb-3 px-2">Finding</th>
                    <th className="text-left pb-3 px-2">Location</th>
                    <th className="text-right pb-3 px-2">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {report.findings?.map((f, i) => (
                    <tr key={i} className="group hover:bg-muted/50 transition-colors">
                      <td className="py-4 px-2">
                        <Badge variant={getSeverityVariant(f.severity)}>{f.severity}</Badge>
                      </td>
                      <td className="py-4 px-2">
                        <p className="font-semibold">{f.message}</p>
                        {f.fix && (
                          <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            Fix: {f.fix}
                          </p>
                        )}
                      </td>
                      <td className="py-4 px-2 font-mono text-xs text-muted-foreground">
                        {f.file}:{f.line}
                      </td>
                      <td className="py-4 px-2 text-right">
                        <span className="font-bold">{f.confidence}%</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
