"use client";

import { useState } from 'react';
import axios from 'axios';
import { Coins, Download, Loader2, CheckCircle } from 'lucide-react';

export default function EquityPage() {
    const [formData, setFormData] = useState({
        employee_id: "",
        vesting_start_date: "",
        number_of_options: 1000,
        vesting_schedule: "4 year vesting, 1 year cliff"
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                employee_id: formData.employee_id,
                vesting_start_date: formData.vesting_start_date,
                number_of_options: Number(formData.number_of_options),
                vesting_schedule: { details: formData.vesting_schedule }
            };

            const response = await axios.post('/api/equity/generate', payload, {
                responseType: 'blob'
            });

            // Download PDF
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Grant_${formData.employee_id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            alert("Equity Grant generated and downloaded!");
        } catch (error) {
            console.error(error);
            alert("Failed to generate equity grant");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-gray-800 flex items-center gap-3">
                <Coins className="text-yellow-500" />
                Equity Management
            </h1>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <h2 className="text-xl font-semibold mb-6">Issue Stock Options</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
                        <input
                            required
                            className="w-full p-2 border rounded-lg"
                            placeholder="e.g. EMP-001"
                            value={formData.employee_id}
                            onChange={e => setFormData({ ...formData, employee_id: e.target.value })}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Vesting Start Date</label>
                            <input
                                required
                                type="date"
                                className="w-full p-2 border rounded-lg"
                                value={formData.vesting_start_date}
                                onChange={e => setFormData({ ...formData, vesting_start_date: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Number of Options</label>
                            <input
                                required
                                type="number"
                                className="w-full p-2 border rounded-lg"
                                value={formData.number_of_options}
                                onChange={e => setFormData({ ...formData, number_of_options: Number(e.target.value) })}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Vesting Schedule</label>
                        <select
                            className="w-full p-2 border rounded-lg"
                            value={formData.vesting_schedule}
                            onChange={e => setFormData({ ...formData, vesting_schedule: e.target.value })}
                        >
                            <option>4 year vesting, 1 year cliff</option>
                            <option>Immediate vesting</option>
                            <option>Performance based</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="animate-spin" /> : <Download className="w-5 h-5" />}
                        Generate Grant Letter
                    </button>
                </form>
            </div>
        </div>
    );
}
