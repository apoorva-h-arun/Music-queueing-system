import React from 'react';
import type { QueueState } from '../types';
import { BarChart3, Database, Layers } from 'lucide-react';

interface MetadataPanelProps {
    queueState: QueueState | null;
}

const MetadataPanel: React.FC<MetadataPanelProps> = ({ queueState }) => {
    return (
        <div className="glass-panel p-6 space-y-6">
            <h2 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-widest">Queue Metadata</h2>

            <div className="grid grid-cols-1 gap-4">
                <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-[var(--accent)]/30 transition-colors">
                    <div className="p-2 bg-[var(--accent)]/10 rounded-lg">
                        <Layers className="w-5 h-5 text-[var(--accent)]" />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase font-black text-[var(--text-muted)] tracking-wider mb-1">Queue Size</p>
                        <p className="text-lg font-bold text-white leading-none">{queueState?.size || 0} Songs</p>
                    </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-[var(--accent)]/30 transition-colors">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <Database className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase font-black text-[var(--text-muted)] tracking-wider mb-1">State Sync</p>
                        <p className="text-lg font-bold text-white leading-none">{queueState?.mode || 'loading'} mode</p>
                    </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-[var(--accent)]/30 transition-colors">
                    <div className="p-2 bg-emerald-500/10 rounded-lg">
                        <BarChart3 className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase font-black text-[var(--text-muted)] tracking-wider mb-1">DSA Engine</p>
                        <p className="text-lg font-bold text-white leading-none">Doubly Linked List</p>
                    </div>
                </div>
            </div>

            <div className="pt-4 border-t border-white/5">
                <p className="text-[10px] text-[var(--text-muted)] italic leading-relaxed">
                    * Priority scores are recalculated in C-core based on usage patterns and user popularity.
                </p>
            </div>
        </div>
    );
};

export default MetadataPanel;
