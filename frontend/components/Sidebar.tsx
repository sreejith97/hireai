import Link from 'next/link';
import { LayoutDashboard, Users, Upload, FileText, Scale, Coins, Sparkles } from 'lucide-react';

const Sidebar = () => {
    const menuItems = [
        { name: 'Dashboard', icon: LayoutDashboard, href: '/' },
        { name: 'Upload Files', icon: Upload, href: '/upload' },
        { name: 'Employees', icon: Users, href: '/employees' },
        { name: 'Documents', icon: Scale, href: '/documents' },
        { name: 'Contracts', icon: FileText, href: '/contracts' },
        { name: 'Equity', icon: Coins, href: '/equity', color: 'text-amber-400' },
    ];

    return (
        <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0">
            {/* Logo Area */}
            <div className="p-6">
                <div className="flex items-center gap-3 px-2">
                    <div className="bg-indigo-600 p-2 rounded-lg shadow-lg shadow-indigo-500/20">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                        HireAi
                    </h1>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-1">
                <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 mt-4">
                    Platform
                </p>
                {menuItems.map((item) => (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group text-sm font-medium ${item.href === '/'
                            ? 'bg-indigo-50 text-indigo-700'
                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                            }`}
                    >
                        <item.icon className={`w-5 h-5 ${item.color || (item.href === '/' ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600')}`} />
                        {item.name}
                    </Link>
                ))}
            </nav>

            {/* User Profile Mock */}
            <div className="p-4 border-t border-slate-100">
                <div className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer">
                    <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300" />
                    <div className="overflow-hidden">
                        <p className="text-sm font-medium text-slate-700 truncate">Admin User</p>
                        <p className="text-xs text-slate-500 truncate">admin@company.com</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
