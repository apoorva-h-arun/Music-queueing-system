import React from 'react';
import { Home, Search, Heart, Radio, MoreHorizontal } from 'lucide-react';

interface SidebarProps {
    currentView: 'home' | 'library';
    onViewChange: (view: 'home' | 'library') => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange }) => {
    return (
        <div className="w-64 bg-[var(--bg-sidebar)] h-full flex flex-col p-6 gap-8">
            <h1 className="text-2xl font-black tracking-tighter text-white px-4">MUSIC PLAYER</h1>

            <nav className="flex flex-col gap-2">
                <button
                    onClick={() => onViewChange('home')}
                    className={`sidebar-link w-full text-left ${currentView === 'home' ? 'text-white bg-[var(--glass)]' : 'text-[var(--text-muted)] hover:text-white'}`}
                >
                    <Home size={20} />
                    <span className="font-semibold">Home</span>
                </button>
                <button
                    onClick={() => onViewChange('library')}
                    className={`sidebar-link w-full text-left ${currentView === 'library' ? 'text-white bg-[var(--glass)]' : 'text-[var(--text-muted)] hover:text-white'}`}
                >
                    <Search size={20} />
                    <span>Your Library</span>
                </button>
            </nav>
        </div>
    );
};

export default Sidebar;
