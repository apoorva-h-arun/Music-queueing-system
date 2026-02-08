import React from 'react';
import { Undo2, Redo2, AlertCircle } from 'lucide-react';

interface UndoRedoControlsProps {
    onUndo: () => void;
    onRedo: () => void;
    loading: boolean;
    mode: string;
}

const UndoRedoControls: React.FC<UndoRedoControlsProps> = ({ onUndo, onRedo, loading, mode }) => {
    const isDemo = mode === 'demo';

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-slate-900 font-bold text-sm flex items-center gap-2">
                    History Core
                </h3>
                {isDemo && (
                    <span className="flex items-center gap-1 text-[10px] bg-amber-50 text-amber-700 px-2 py-0.5 rounded border border-amber-100">
                        <AlertCircle className="w-3 h-3" />
                        C-LIB REQUIRED
                    </span>
                )}
            </div>

            <div className="grid grid-cols-2 gap-3">
                <button
                    onClick={onUndo}
                    disabled={loading || isDemo}
                    className="flex items-center justify-center gap-2 py-2.5 px-4 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50 transition-all font-bold text-sm shadow-sm disabled:opacity-40 disabled:hover:bg-white"
                >
                    <Undo2 className="w-4 h-4" />
                    Undo
                </button>
                <button
                    onClick={onRedo}
                    disabled={loading || isDemo}
                    className="flex items-center justify-center gap-2 py-2.5 px-4 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50 transition-all font-bold text-sm shadow-sm disabled:opacity-40 disabled:hover:bg-white"
                >
                    <Redo2 className="w-4 h-4" />
                    Redo
                </button>
            </div>

            {isDemo && (
                <p className="text-[10px] text-slate-500 italic mt-2">
                    Undo/Redo stack operations require the compiled C library for full DSA execution.
                </p>
            )}
        </div>
    );
};

export default UndoRedoControls;
