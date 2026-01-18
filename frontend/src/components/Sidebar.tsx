import { Home } from 'lucide-react';

interface SidebarProps {
}

const Sidebar: React.FC<SidebarProps> = () => {
    return (
        <div className="w-64 bg-[var(--bg-sidebar)] h-full flex flex-col p-6 gap-8">
            <h1 className="text-2xl font-black tracking-tighter text-white px-4">MUSIC PLAYER</h1>

            <nav className="flex flex-col gap-2">
                <button
                    className="sidebar-link w-full text-left text-white bg-[var(--glass)]"
                >
                    <Home size={20} />
                    <span className="font-semibold">Home</span>
                </button>
            </nav>
        </div>
    );
};

export default Sidebar;
