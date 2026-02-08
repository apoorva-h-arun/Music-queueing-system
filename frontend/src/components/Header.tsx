import React from 'react';
import { Search, Music2 } from 'lucide-react';

interface HeaderProps {
    searchQuery: string;
    onSearchChange: (query: string) => void;
}

const Header: React.FC<HeaderProps> = ({ searchQuery, onSearchChange }) => {
    return (
        <header className="bg-[var(--bg-sidebar)] border-b border-white/5 p-4 flex items-center justify-between gap-8 h-20">
            <div className="flex items-center gap-3 min-w-fit">
                <div className="bg-[var(--accent)] p-2 rounded-lg text-[var(--bg-main)]">
                    <Music2 className="w-6 h-6" />
                </div>
                <div>
                    <h1 className="text-xl font-bold tracking-tight text-white">
                        Music Queue
                    </h1>
                </div>
            </div>

            <div className="flex-1 max-w-2xl relative group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)] group-focus-within:text-[var(--accent)] transition-colors" size={20} />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => onSearchChange(e.target.value)}
                    placeholder="Search songs, artists..."
                    className="w-full bg-white/5 border border-white/10 rounded-full py-3 pl-12 pr-4 text-white focus:outline-none focus:border-[var(--accent)] focus:bg-white/10 transition-all placeholder:text-[var(--text-muted)]"
                />
            </div>

            <div className="hidden md:flex items-center gap-4 min-w-fit">
                <div className="text-right">
                    <span className="block text-xs font-semibold text-[var(--text-muted)] uppercase">System Status</span>
                    <span className="flex items-center gap-1.5 text-sm font-medium text-green-500">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        Online
                    </span>
                </div>
            </div>
        </header>
    );
};

export default Header;
