import React from 'react';
import { Music2 } from 'lucide-react';

const Header: React.FC = () => {
    return (
        <header className="bg-white border-b border-slate-200">
            <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="bg-blue-600 p-2 rounded-lg text-white">
                        <Music2 className="w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-tight text-slate-900">
                            Music Streaming Queue Manager
                        </h1>
                        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                            Priority-Based Queue System • DSA Laboratory
                        </p>
                    </div>
                </div>

                <div className="hidden md:flex items-center gap-4">
                    <div className="text-right">
                        <span className="block text-xs font-semibold text-slate-400 uppercase">System Status</span>
                        <span className="flex items-center gap-1.5 text-sm font-medium text-green-600">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            CORE CONNECTED
                        </span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
