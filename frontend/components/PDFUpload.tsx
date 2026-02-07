"use client";

import { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface PDFUploadProps {
    endpoint: string;
    label: string;
    paramName?: string; // e.g., 'country' or 'company_id'
    paramLabel?: string;
    onSuccess?: (data: any) => void;
}

export default function PDFUpload({ endpoint, label, paramName = "country", paramLabel = "Country", onSuccess }: PDFUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [paramValue, setParamValue] = useState("");
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        if (paramValue) {
            formData.append(paramName, paramValue);
        }

        try {
            const response = await axios.post(`/api${endpoint}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setResult(response.data);
            if (onSuccess) onSuccess(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Upload failed.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="font-semibold text-lg mb-4 text-gray-800 flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-500" />
                {label}
            </h3>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{paramLabel}</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder={`Enter ${paramLabel}...`}
                        value={paramValue}
                        onChange={(e) => setParamValue(e.target.value)}
                    />
                </div>

                <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:bg-gray-50 transition-colors">
                    <input
                        type="file"
                        accept="application/pdf"
                        className="hidden"
                        id={`file-${label}`}
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                    <label htmlFor={`file-${label}`} className="cursor-pointer block">
                        {file ? (
                            <div className="text-blue-600 font-medium flex items-center justify-center gap-2">
                                <FileText className="w-4 h-4" /> {file.name}
                            </div>
                        ) : (
                            <span className="text-gray-500 text-sm">Click to select PDF</span>
                        )}
                    </label>
                </div>

                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className={`w-full py-2 rounded-lg flex items-center justify-center gap-2 font-medium transition-all
                ${!file || uploading ? 'bg-gray-100 text-gray-400' : 'bg-blue-600 text-white hover:bg-blue-700'}
            `}
                >
                    {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                    {uploading ? "Processing..." : "Upload & Extract"}
                </button>

                {result && (
                    <div className="p-3 bg-green-50 text-green-700 text-sm rounded-lg flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 mt-0.5" />
                        <div>
                            <p className="font-semibold">Success!</p>
                            <p>Extracted {result.clauses_count} clauses.</p>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 mt-0.5" />
                        <span>{error}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
