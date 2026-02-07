"use client";

import { useState } from 'react';
import axios from 'axios';
import { Upload as UploadIcon, FileSpreadsheet, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/api/employees/upload_excel', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-2 text-gray-800">Upload Employees</h1>
            <p className="text-gray-500 mb-8">Upload your employee Excel sheet (xlsx) to populate the database.</p>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center text-center hover:border-blue-400 transition-colors bg-gray-50/50">
                    <FileSpreadsheet className="w-12 h-12 text-blue-500 mb-4" />

                    <input
                        type="file"
                        accept=".xlsx, .xls"
                        onChange={handleFileChange}
                        className="hidden"
                        id="file-upload"
                    />

                    <label htmlFor="file-upload" className="cursor-pointer">
                        <span className="text-blue-600 font-medium hover:underline">Click to upload</span>
                        <span className="text-gray-500"> or drag and drop</span>
                    </label>
                    <p className="text-xs text-gray-400 mt-2">XLSX files only</p>

                    {file && (
                        <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded-lg text-sm flex items-center gap-2">
                            <FileSpreadsheet className="w-4 h-4" />
                            {file.name}
                        </div>
                    )}
                </div>

                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className={`w-full mt-6 py-3 px-4 rounded-lg flex items-center justify-center gap-2 font-medium transition-all
            ${!file || uploading
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg'
                        }`}
                >
                    {uploading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Processing...
                        </>
                    ) : (
                        <>
                            <UploadIcon className="w-5 h-5" />
                            Upload Employees
                        </>
                    )}
                </button>

                {result && (
                    <div className="mt-6 p-4 bg-green-50 border border-green-100 rounded-lg text-green-800 flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 mt-0.5 text-green-600" />
                        <div>
                            <p className="font-semibold">Upload Successful!</p>
                            <p className="text-sm mt-1">Processed {result.total_parsed} rows. Saved {result.saved_count} new employees.</p>
                            {result.errors && result.errors.length > 0 && (
                                <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                                    <p className="font-semibold mb-1">Items with errors:</p>
                                    <ul className="list-disc pl-4">
                                        {result.errors.slice(0, 3).map((e: any, i: number) => <li key={i}>{e}</li>)}
                                        {result.errors.length > 3 && <li>...and {result.errors.length - 3} more</li>}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-100 rounded-lg text-red-800 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 mt-0.5 text-red-600" />
                        <div>
                            <p className="font-semibold">Upload Failed</p>
                            <p className="text-sm mt-1">{error}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
