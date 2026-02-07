"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';
import PDFUpload from '@/components/PDFUpload';
import { Book, Shield, RefreshCw } from 'lucide-react';

export default function DocumentsPage() {
    const [clauses, setClauses] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [filterType, setFilterType] = useState("");
    const [filterCountry, setFilterCountry] = useState("");

    const fetchClauses = async () => {
        setLoading(true);
        try {
            const res = await axios.get('/api/clauses', {
                params: {
                    country: filterCountry || undefined,
                    clause_type: filterType || undefined
                }
            });
            setClauses(res.data);
        } catch (error) {
            console.error("Failed to fetch clauses", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClauses();
    }, []);

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-gray-800">Document Management</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                <PDFUpload
                    label="Upload Labor Law"
                    endpoint="/legal/pdf/upload"
                    paramName="country"
                    paramLabel="Country (e.g., UAE)"
                    onSuccess={fetchClauses}
                />
                <PDFUpload
                    label="Upload Company Policy"
                    endpoint="/policies/pdf/upload"
                    paramName="company_id"
                    paramLabel="Company ID (e.g., TechCorp)"
                    onSuccess={fetchClauses}
                />
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-800">Extracted Clauses Database</h2>
                    <div className="flex gap-2">
                        <input
                            placeholder="Filter Country..."
                            className="p-2 border rounded-lg text-sm"
                            value={filterCountry}
                            onChange={e => setFilterCountry(e.target.value)}
                        />
                        <button
                            onClick={fetchClauses}
                            className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-50 text-gray-500 font-medium">
                            <tr>
                                <th className="p-4">Type</th>
                                <th className="p-4 w-1/2">Text Content</th>
                                <th className="p-4">Variables</th>
                                <th className="p-4">Country/ID</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {clauses.map((clause) => (
                                <tr key={clause.id || Math.random()} className="hover:bg-gray-50">
                                    <td className="p-4">
                                        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-semibold">
                                            {clause.clause_type}
                                        </span>
                                    </td>
                                    <td className="p-4 text-gray-700 line-clamp-2 max-w-sm truncate">{clause.text}</td>
                                    <td className="p-4 text-gray-500 font-mono text-xs max-w-xs break-all">
                                        {JSON.stringify(clause.variables)}
                                    </td>
                                    <td className="p-4 text-gray-600">{clause.country || '-'}</td>
                                </tr>
                            ))}
                            {clauses.length === 0 && !loading && (
                                <tr>
                                    <td colSpan={4} className="p-8 text-center text-gray-400">
                                        No clauses found. Upload documents to populate.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
