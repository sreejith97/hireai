"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';
import { FileText, Download, Plus, Loader2, Check } from 'lucide-react';

export default function ContractsPage() {
    const [contracts, setContracts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // New Template Form
    const [showNew, setShowNew] = useState(false);
    const [newCompany, setNewCompany] = useState("");
    const [newCountry, setNewCountry] = useState("UAE");
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        fetchContracts();
    }, []);

    const fetchContracts = async () => {
        try {
            const res = await axios.get('/api/contracts');
            setContracts(res.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const createTemplate = async () => {
        if (!newCompany || !newCountry) return;
        setCreating(true);
        try {
            await axios.post('/api/contracts/generate/legal', {
                company_id: newCompany,
                country: newCountry
            });
            await fetchContracts();
            setShowNew(false);
            setNewCompany("");
        } catch (e) {
            alert("Failed to create template. Ensure PDF laws/policies are uploaded first.");
        } finally {
            setCreating(false);
        }
    };

    const downloadPdf = async (id: string, name: string) => {
        try {
            const response = await axios.get(`/api/contracts/${id}/pdf`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Contract_${name}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (e) {
            console.error("Download failed", e);
            alert("Download failed. Is this an employment contract?");
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800">Contracts</h1>
                <button
                    onClick={() => setShowNew(!showNew)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    <Plus className="w-4 h-4" /> New Template
                </button>
            </div>

            {showNew && (
                <div className="bg-white p-6 rounded-xl shadow-lg border border-blue-100 mb-8 max-w-lg">
                    <h2 className="font-semibold text-lg mb-4">Create Legal Template</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Company ID</label>
                            <input
                                className="w-full p-2 border rounded-lg"
                                placeholder="e.g., TechCorp"
                                value={newCompany}
                                onChange={e => setNewCompany(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                            <input
                                className="w-full p-2 border rounded-lg"
                                placeholder="e.g., UAE"
                                value={newCountry}
                                onChange={e => setNewCountry(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2 justify-end mt-4">
                            <button onClick={() => setShowNew(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
                            <button
                                onClick={createTemplate}
                                disabled={creating}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                            >
                                {creating && <Loader2 className="w-4 h-4 animate-spin" />}
                                Generate Draft
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Templates Section */}
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Legal Templates (Drafts)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {contracts.filter(c => c.contract_type === "legal").map(c => (
                    <div key={c._id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start mb-2">
                            <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-semibold">TEMPLATE</span>
                            <span className="text-xs text-gray-400 font-mono">ID: {c._id.slice(-6)}</span>
                        </div>
                        <h3 className="font-bold text-gray-900">{c.company_id} Template</h3>
                        <p className="text-sm text-gray-500 mb-4">{new Date(c.created_at || Date.now()).toLocaleDateString()}</p>
                        <div className="text-xs text-gray-400">
                            Does not differentiate between countries in UI yet, but tracks ID.
                        </div>
                    </div>
                ))}
                {contracts.filter(c => c.contract_type === "legal").length === 0 && !loading && (
                    <div className="text-gray-400 italic col-span-full">No templates created.</div>
                )}
            </div>

            {/* Generated Contracts Section */}
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Generated Employment Contracts</h2>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium text-sm">
                        <tr>
                            <th className="p-4">Candidate</th>
                            <th className="p-4">Company</th>
                            <th className="p-4">Version</th>
                            <th className="p-4">Date</th>
                            <th className="p-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {contracts.filter(c => c.contract_type === "employment").map(c => (
                            <tr key={c._id} className="hover:bg-gray-50">
                                <td className="p-4 font-medium text-gray-900">
                                    {c.candidate_name || "Unknown"}
                                    {c.parent_contract_id && <span className="ml-2 text-xs text-gray-400">(Renewed)</span>}
                                </td>
                                <td className="p-4 text-gray-600">{c.company_id}</td>
                                <td className="p-4 text-gray-600">
                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${c.status === 'active' || c.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                        v{c.version || 1}
                                    </span>
                                </td>
                                <td className="p-4 text-gray-600">{new Date(c.created_at || Date.now()).toLocaleDateString()}</td>
                                <td className="p-4 flex gap-2">
                                    <button
                                        onClick={() => downloadPdf(c._id, c.candidate_name)}
                                        className="text-blue-600 hover:text-blue-800"
                                        title="Download PDF"
                                    >
                                        <Download className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={async () => {
                                            const newDate = prompt("Enter new end date (YYYY-MM-DD):");
                                            if (newDate) {
                                                await axios.post(`/api/contracts/${c._id}/renew`, { new_end_date: newDate });
                                                fetchContracts();
                                            }
                                        }}
                                        className="text-green-600 hover:text-green-800"
                                        title="Renew Contract"
                                    >
                                        <Loader2 className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={async () => {
                                            const key = prompt("Enter text to replace:");
                                            const val = key ? prompt("Enter new text:") : null;
                                            if (key && val) {
                                                await axios.post(`/api/contracts/${c._id}/amend`, { amendments: { [key]: val } });
                                                fetchContracts();
                                            }
                                        }}
                                        className="text-orange-600 hover:text-orange-800"
                                        title="Amend Contract"
                                    >
                                        <FileText className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {contracts.filter(c => c.contract_type === "employment").length === 0 && !loading && (
                            <tr><td colSpan={5} className="p-8 text-center text-gray-400">No generated contracts found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
