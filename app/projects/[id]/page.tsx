'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useDatasets, useProjects, Dataset, Project } from '@/hooks/useDataApi';
import { Folder, Upload, FileText } from 'lucide-react';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = Array.isArray(params?.id) ? params.id[0] : params?.id;
  const { getProject } = useProjects();
  const { listDatasets, uploadDataset } = useDatasets(projectId || '');
  const [project, setProject] = useState<Project | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;

    const loadProject = async () => {
      try {
        setLoading(true);
        const [projectData, datasetData] = await Promise.all([
          getProject(projectId),
          listDatasets(),
        ]);
        if (cancelled) return;
        setProject(projectData);
        setDatasets(datasetData);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load project');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadProject();
    return () => {
      cancelled = true;
    };
  }, [getProject, listDatasets, projectId]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    try {
      const dataset = await uploadDataset(selectedFile);
      setDatasets([dataset, ...datasets]);
      setSelectedFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (!projectId) {
    return null;
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          {error && (
            <Card className="p-4 mb-6 border border-red-200 bg-red-50 text-red-700">
              {error}
            </Card>
          )}

          {loading ? (
            <Card className="p-8 text-center text-slate-600">Loading project...</Card>
          ) : project ? (
            <>
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
                <div>
                  <div className="flex items-center gap-2 text-slate-500 text-sm mb-2">
                    <button className="hover:text-slate-700" onClick={() => router.push('/projects')}>
                      Projects
                    </button>
                    <span>/</span>
                    <span className="text-slate-700">{project.name}</span>
                  </div>
                  <h1 className="text-3xl font-bold text-slate-900">{project.name}</h1>
                  {project.description && (
                    <p className="text-slate-600 mt-2">{project.description}</p>
                  )}
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={() => router.push('/upload')}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Quick Upload
                  </Button>
                </div>
              </div>

              <Card className="p-6 mb-8">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">Upload Dataset</h2>
                    <p className="text-sm text-slate-600">Attach a dataset to this project</p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} />
                    <Button
                      onClick={handleUpload}
                      disabled={!selectedFile || uploading}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {uploading ? 'Uploading...' : 'Upload'}
                    </Button>
                  </div>
                </div>
                {selectedFile && (
                  <div className="mt-3 text-sm text-slate-600">
                    Selected: <span className="font-medium text-slate-900">{selectedFile.name}</span>
                  </div>
                )}
              </Card>

              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Folder className="h-5 w-5 text-blue-600" />
                    <h2 className="text-lg font-semibold text-slate-900">Dataset History</h2>
                  </div>
                  <span className="text-sm text-slate-500">{datasets.length} datasets</span>
                </div>

                {datasets.length === 0 ? (
                  <div className="text-center py-10 text-slate-500">
                    No datasets uploaded yet.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="text-left px-4 py-3 text-slate-600">Dataset</th>
                          <th className="text-left px-4 py-3 text-slate-600">Uploaded</th>
                          <th className="text-left px-4 py-3 text-slate-600">Size</th>
                          <th className="text-left px-4 py-3 text-slate-600">Health</th>
                          <th className="text-right px-4 py-3 text-slate-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {datasets.map((dataset) => (
                          <tr key={dataset.id} className="border-b">
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-slate-400" />
                                <span className="font-medium text-slate-900">{dataset.filename}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                              {new Date(dataset.upload_date).toLocaleDateString()}
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                              {Math.round(dataset.size_bytes / 1024)} KB
                            </td>
                            <td className="px-4 py-3 text-slate-600">
                              {typeof dataset.health_score === 'number' ? `${Math.round(dataset.health_score)}%` : '—'}
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => router.push(`/analysis?datasetId=${dataset.id}`)}
                              >
                                View Analysis
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            </>
          ) : (
            <Card className="p-8 text-center text-slate-600">Project not found.</Card>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
