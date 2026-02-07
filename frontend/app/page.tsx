"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, FileText, Clock, ArrowRight, Activity, Sparkles, TrendingUp, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const [stats, setStats] = useState({
    employees: 0,
    contracts: 0,
    pending: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const empRes = await axios.get('http://localhost:8000/employees');
        setStats(prev => ({ ...prev, employees: empRes.data.length }));
      } catch (error) {
        console.error("Failed to fetch stats", error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="min-h-full font-sans selection:bg-indigo-100">

      <div className="p-8 max-w-7xl mx-auto">

        {/* Header */}
        <header className="mb-10 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 mb-2">Dashboard</h1>
            <p className="text-slate-500">Welcome back, Admin. Here's what's happening today.</p>
          </div>
          <div className="flex gap-4">
            <button className="flex items-center gap-2 bg-white border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 text-slate-600 px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm hover:shadow-md active:scale-95">
              <Sparkles className="w-4 h-4" />
              Ask AI Assistant
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {/* Active Employees Card */}
          <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-8">
              <div className="p-3 bg-indigo-50 rounded-xl">
                <Users className="w-6 h-6 text-indigo-600" />
              </div>
              <div className="flex items-center gap-1 text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg text-xs font-medium">
                <TrendingUp className="w-3 h-3" />
                +12%
              </div>
            </div>

            <div>
              <h3 className="text-slate-500 text-sm font-medium mb-1">Total Employees</h3>
              <div className="flex items-end gap-3">
                <p className="text-4xl font-bold text-slate-900 tracking-tight">{stats.employees}</p>
                <span className="text-slate-400 mb-1.5 text-sm">Active</span>
              </div>
            </div>
          </div>

          {/* Contracts Card */}
          <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-8">
              <div className="p-3 bg-emerald-50 rounded-xl">
                <FileText className="w-6 h-6 text-emerald-600" />
              </div>
            </div>

            <div>
              <h3 className="text-slate-500 text-sm font-medium mb-1">Contracts Generated</h3>
              <div className="flex items-end gap-3">
                <p className="text-4xl font-bold text-slate-900 tracking-tight">{stats.contracts}</p>
                <span className="text-slate-400 mb-1.5 text-sm">Documents</span>
              </div>
            </div>
          </div>

          {/* Pending Actions Card */}
          <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-8">
              <div className="p-3 bg-amber-50 rounded-xl">
                <Clock className="w-6 h-6 text-amber-600" />
              </div>
              <div className="flex items-center gap-1 text-slate-600 bg-slate-100 px-2 py-1 rounded-lg text-xs font-medium">
                <ShieldCheck className="w-3 h-3" />
                Review
              </div>
            </div>

            <div>
              <h3 className="text-slate-500 text-sm font-medium mb-1">Pending Actions</h3>
              <div className="flex items-end gap-3">
                <p className="text-4xl font-bold text-slate-900 tracking-tight">{stats.pending}</p>
                <span className="text-slate-400 mb-1.5 text-sm">To Review</span>
              </div>
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Quick Actions Panel */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-semibold mb-6 text-slate-900 flex items-center gap-2">
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link href="/employees/upload" className="group p-5 bg-slate-50 border border-slate-100 rounded-xl hover:bg-white hover:border-indigo-200 hover:shadow-md transition-all duration-300 flex flex-col gap-4">
                <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center group-hover:bg-indigo-50 group-hover:border-indigo-100 transition-colors">
                  <Users className="w-5 h-5 text-slate-600 group-hover:text-indigo-600" />
                </div>
                <div>
                  <span className="block font-medium text-slate-900 mb-1 group-hover:text-indigo-700">Onboard Employee</span>
                  <span className="text-xs text-slate-500">Upload CSV/Excel data</span>
                </div>
              </Link>

              <Link href="/contracts" className="group p-5 bg-slate-50 border border-slate-100 rounded-xl hover:bg-white hover:border-emerald-200 hover:shadow-md transition-all duration-300 flex flex-col gap-4">
                <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center group-hover:bg-emerald-50 group-hover:border-emerald-100 transition-colors">
                  <FileText className="w-5 h-5 text-slate-600 group-hover:text-emerald-600" />
                </div>
                <div>
                  <span className="block font-medium text-slate-900 mb-1 group-hover:text-emerald-700">Draft Contract</span>
                  <span className="text-xs text-slate-500">Generate legal documents</span>
                </div>
              </Link>
            </div>
          </div>

          {/* System Status / Activity */}
          <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
            <h2 className="text-lg font-semibold mb-6 text-slate-900">System Status</h2>
            <div className="space-y-6">
              {/* Mock Status Items */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-sm text-slate-600">Database</span>
                </div>
                <span className="text-xs text-emerald-700 font-mono bg-emerald-50 px-2 py-0.5 rounded">ONLINE</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-sm text-slate-600">LLM Inference</span>
                </div>
                <span className="text-xs text-emerald-700 font-mono bg-emerald-50 px-2 py-0.5 rounded">READY</span>
              </div>

              <div className="h-px bg-slate-100 my-4" />

              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">Storage</p>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full w-[35%] bg-indigo-500 rounded-full" />
                </div>
                <div className="flex justify-between mt-2 text-xs text-slate-500">
                  <span>35% Used</span>
                  <span>500GB Available</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
