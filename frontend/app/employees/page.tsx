"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';
import { FileText, Search, Loader2, Download, Plus } from 'lucide-react';

export default function EmployeesPage() {
    const [employees, setEmployees] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [contracts, setContracts] = useState<any[]>([]);
    const [selectedEmp, setSelectedEmp] = useState<any>(null);
    const [generating, setGenerating] = useState(false);
    const [legalContractId, setLegalContractId] = useState("");
    const [successMsg, setSuccessMsg] = useState("");

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [empRes, contRes] = await Promise.all([
                axios.get('/api/employees'),
                axios.get('/api/contracts?contract_type=legal') // Fetch drafts/templates
            ]);
            setEmployees(empRes.data);
            setContracts(contRes.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const generateContract = async () => {
        if (!selectedEmp || !legalContractId) return;
        setGenerating(true);
        setSuccessMsg("");

        try {
            const payload = {
                legal_contract_id: legalContractId,
                candidate: {
                    name: selectedEmp.name,
                    role: selectedEmp.role || "Employee",
                    salary: selectedEmp.salary || "0",
                    start_date: selectedEmp.start_date || new Date().toISOString().split('T')[0]
                }
            };

            const res = await axios.post('/api/contracts/generate/employment', payload);
            setSuccessMsg(`Contract generated! ID: ${res.data.employment_contract_id}`);

            // Optionally download immediately or show link
            setTimeout(() => {
                setSelectedEmp(null);
                setSuccessMsg("");
            }, 3000);

        } catch (e) {
            alert("Failed to generate contract");
            console.error(e);
        } finally {
            setGenerating(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading employees...</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800">Employees</h1>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                        <Search className="w-4 h-4" /> Filter
                    </button>
                    <a href="/upload" className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        <Plus className="w-4 h-4" /> Add New
                    </a>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium text-sm">
                        <tr>
                            <th className="p-4">Name</th>
                            <th className="p-4">Role</th>
                            <th className="p-4">Email</th>
                            <th className="p-4">Start Date</th>
                            <th className="p-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {employees.map((emp) => (
                            <tr key={emp._id} className="hover:bg-gray-50">
                                <td className="p-4 font-medium text-gray-900">{emp.name}</td>
                                <td className="p-4 text-gray-600">{emp.role || '-'}</td>
                                <td className="p-4 text-gray-600">{emp.email || '-'}</td>
                                <td className="p-4 text-gray-600">{emp.start_date || '-'}</td>
                                <td className="p-4">
                                    <button
                                        onClick={() => setSelectedEmp(emp)}
                                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
                                    >
                                        <FileText className="w-4 h-4" />
                                        Generate Contract
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {employees.length === 0 && (
                            <tr>
                                <td colSpan={5} className="p-8 text-center text-gray-500">No employees found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Modal */}
            {selectedEmp && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
                        <h2 className="text-xl font-bold mb-4">Generate Contract</h2>
                        <p className="text-gray-600 mb-4">
                            Creating employment contract for <span className="font-semibold">{selectedEmp.name}</span>.
                        </p>

                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">Select Contract Template</label>
                            <select
                                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                value={legalContractId}
                                onChange={(e) => setLegalContractId(e.target.value)}
                            >
                                <option value="">-- Select a Template --</option>
                                {contracts.map(c => (
                                    <option key={c._id} value={c._id}>
                                        Draft {c._id} ({c.contract_type})
                                    </option>
                                ))}
                            </select>
                            {contracts.length === 0 && (
                                <p className="text-xs text-red-500 mt-1">No legal contract templates found. Please generate one first.</p>
                            )}
                        </div>

                        {successMsg && (
                            <div className="mb-4 p-3 bg-green-50 text-green-700 text-sm rounded-lg flex items-center gap-2">
                                <CheckCircle className="w-4 h-4" /> {successMsg}
                            </div>
                        )}

                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => setSelectedEmp(null)}
                                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={generateContract}
                                disabled={!legalContractId || generating}
                                className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2
                        ${(!legalContractId || generating) ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                            >
                                {generating && <Loader2 className="w-4 h-4 animate-spin" />}
                                Generate
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function CheckCircle({ className }: { className?: string }) {
    return (
        <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
    )
}
