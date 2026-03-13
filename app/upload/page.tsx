'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Upload, File, X } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { useProjects, useDatasets, Project } from '@/hooks/useDataApi';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';

export default function UploadPage() {
  const router = useRouter();
  const { listProjects } = useProjects();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { uploadDataset } = useDatasets(selectedProjectId);

  useEffect(() => {
    let cancelled = false;

    const loadProjects = async () => {
      try {
        const data = await listProjects();
        if (!cancelled) setProjects(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load projects');
        }
      }
    };

    loadProjects();
    return () => {
      cancelled = true;
    };
  }, [listProjects]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        setUploadedFile(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setUploadedFile(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      let uploadedDatasetId: string | null = null;
      if (selectedProjectId) {
        const dataset = await uploadDataset(uploadedFile);
        uploadedDatasetId = dataset.id;
        localStorage.setItem('uploadedDatasetId', dataset.id);
      } else {
        localStorage.removeItem('uploadedDatasetId');
      }

      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const arrayBuffer = event.target?.result as ArrayBuffer;
          const fileData = {
            name: uploadedFile.name,
            type: uploadedFile.type,
            data: Array.from(new Uint8Array(arrayBuffer)),
            timestamp: Date.now(),
          };
          localStorage.setItem('uploadedFile', JSON.stringify(fileData));
          console.log("File stored in localStorage:", uploadedFile.name);
          
          // Small delay to ensure storage is complete
          setTimeout(() => {
            setIsUploading(false);
            router.push("/preview");
          }, 100);
        } catch (error) {
          console.error("Storage error:", error);
          setIsUploading(false);
        }
      };
      
      reader.onerror = () => {
        console.error("File read error");
        setIsUploading(false);
      };
      
      reader.readAsArrayBuffer(uploadedFile);
    } catch (error) {
      console.error("Upload failed:", error);
      setError(error instanceof Error ? error.message : 'Upload failed');
      setIsUploading(false);
    }
  };
  const removeFile = () => {
    setUploadedFile(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Upload Dataset</h1>
          <p className="text-slate-600">Upload your CSV or Excel file to get started with data quality analysis</p>
        </div>

        {error && (
          <Card className="p-4 mb-6 border border-red-200 bg-red-50 text-red-700">
            {error}
          </Card>
        )}

        <Card className="p-6 mb-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-3">Attach to Project (Optional)</h2>
          <div className="grid gap-2">
            <label className="text-xs text-slate-500">Project</label>
            <select
              value={selectedProjectId}
              onChange={(event) => setSelectedProjectId(event.target.value)}
              className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-slate-500">Datasets will appear under the chosen project.</p>
          </div>
        </Card>

        <Card className="p-8">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-slate-300 bg-slate-50'
            }`}
          >
            <div className="flex flex-col items-center">
              <div className="p-4 bg-blue-100 rounded-full mb-4">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>

              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                Drop your file here
              </h3>

              <p className="text-slate-600 mb-4">
                or click to browse
              </p>

              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />

              <label htmlFor="file-upload">
                <Button variant="outline" className="cursor-pointer" asChild>
                  <span>Browse Files</span>
                </Button>
              </label>

              <p className="text-sm text-slate-500 mt-4">
                Supported formats: CSV, Excel (.xlsx, .xls)
              </p>
            </div>
          </div>

          {uploadedFile && (
            <div className="mt-6">
              <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded">
                    <File className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">{uploadedFile.name}</p>
                    <p className="text-sm text-slate-600">{formatFileSize(uploadedFile.size)}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={removeFile}
                  className="text-slate-600 hover:text-slate-900"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex justify-end mt-6">
                <Button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="bg-blue-500 hover:bg-blue-600"
                >
                  {isUploading ? 'Uploading...' : 'Continue to Preview'}
                </Button>
              </div>
            </div>
          )}
        </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
