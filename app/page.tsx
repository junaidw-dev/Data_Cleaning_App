'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';
import { useProjects, Project, Dataset } from '@/hooks/useDataApi';
import { useApiClient } from '@/hooks/useApiClient';
import { Activity, Folder, Upload, TrendingUp, Database, CheckCircle, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

export default function LandingPage() {
  const router = useRouter();
  const { listProjects } = useProjects();
  const { apiCall } = useApiClient();
  const [projects, setProjects] = useState<Project[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadOverview = async () => {
      setLoading(true);
      setError(null);
      try {
        const projectData = await listProjects();
        if (cancelled) return;

        setProjects(projectData);

        const recentProjects = [...projectData]
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 3);

        if (recentProjects.length === 0) {
          setDatasets([]);
          return;
        }

        const datasetLists = await Promise.all(
          recentProjects.map((project) => apiCall<Dataset[]>(`/api/projects/${project.id}/datasets`))
        );

        if (cancelled) return;

        const flattened = datasetLists.flat();
        setDatasets(flattened);
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : 'Failed to load dashboard data';
        setError(message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadOverview();
    return () => {
      cancelled = true;
    };
  }, [apiCall, listProjects]);

  const totalDatasets = useMemo(() => {
    return projects.reduce((sum, project) => sum + project.dataset_count, 0);
  }, [projects]);

  const averageHealthScore = useMemo(() => {
    const scores = datasets
      .map((dataset) => dataset.health_score)
      .filter((score): score is number => typeof score === 'number');
    if (scores.length === 0) return null;
    const avg = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    return Math.round(avg);
  }, [datasets]);

  const recentProjects = useMemo(() => {
    return [...projects]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
  }, [projects]);

  const recentDatasets = useMemo(() => {
    return [...datasets]
      .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
      .slice(0, 5);
  }, [datasets]);

  const projectNameById = useMemo(() => {
    return projects.reduce<Record<string, string>>((acc, project) => {
      acc[project.id] = project.name;
      return acc;
    }, {});
  }, [projects]);

  // Data for visualizations
  const healthScoreDistribution = useMemo(() => {
    const excellent = datasets.filter(d => d.health_score >= 80).length;
    const good = datasets.filter(d => d.health_score >= 60 && d.health_score < 80).length;
    const fair = datasets.filter(d => d.health_score >= 40 && d.health_score < 60).length;
    const poor = datasets.filter(d => d.health_score < 40).length;
    return [
      { name: 'Excellent', value: excellent, color: '#10b981' },
      { name: 'Good', value: good, color: '#3b82f6' },
      { name: 'Fair', value: fair, color: '#f59e0b' },
      { name: 'Poor', value: poor, color: '#ef4444' },
    ];
  }, [datasets]);

  const datasetTrend = useMemo(() => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date;
    });

    return last7Days.map((date) => {
      const count = datasets.filter((d) => {
        const uploadDate = new Date(d.upload_date);
        return uploadDate.toDateString() === date.toDateString();
      }).length;
      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        datasets: count,
      };
    });
  }, [datasets]);

  const projectsWithDatasets = useMemo(() => {
    return projects.slice(0, 8).map(p => ({
      name: p.name.length > 15 ? p.name.substring(0, 15) + '...' : p.name,
      datasets: p.dataset_count
    }));
  }, [projects]);

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
              <p className="text-slate-600 mt-1">Monitor your data quality workspace</p>
            </div>
            <Button
              onClick={() => router.push('/upload')}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload Dataset
            </Button>
          </div>

          {error && (
            <Card className="p-4 mb-6 border border-red-200 bg-red-50 text-red-700">
              {error}
            </Card>
          )}

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Projects</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{projects.length}</p>
                  <p className="text-xs text-slate-500 mt-2">Active workspaces</p>
                </div>
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Folder className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Datasets</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{totalDatasets}</p>
                  <p className="text-xs text-slate-500 mt-2">Analyzed & processed</p>
                </div>
                <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Database className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Avg Health Score</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">
                    {averageHealthScore === null ? '—' : `${averageHealthScore}%`}
                  </p>
                  <p className="text-xs text-slate-500 mt-2">Data quality rating</p>
                </div>
                <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">This Month</p>
                  <p className="text-3xl font-bold text-slate-900 mt-2">{datasets.filter(d => {
                    const date = new Date(d.upload_date);
                    const today = new Date();
                    return date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
                  }).length}</p>
                  <p className="text-xs text-slate-500 mt-2">New datasets</p>
                </div>
                <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid lg:grid-cols-3 gap-6 mb-8">
            {/* Dataset Trend */}
            <Card className="p-6 lg:col-span-2 border border-slate-100">
              <h2 className="font-semibold text-slate-900 mb-4">Dataset Upload Trend</h2>
              {loading ? (
                <p className="text-sm text-slate-500">Loading chart...</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={datasetTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }} />
                    <Line type="monotone" dataKey="datasets" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Card>

            {/* Health Score Distribution */}
            <Card className="p-6 border border-slate-100">
              <h2 className="font-semibold text-slate-900 mb-4">Health Score Distribution</h2>
              {loading ? (
                <p className="text-sm text-slate-500">Loading chart...</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={healthScoreDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {healthScoreDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
              <div className="mt-4 space-y-2">
                {healthScoreDistribution.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                      <span className="text-slate-600">{item.name}</span>
                    </div>
                    <span className="font-medium text-slate-900">{item.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Projects & Datasets Bar Chart */}
          {projects.length > 0 && (
            <Card className="p-6 border border-slate-100 mb-8">
              <h2 className="font-semibold text-slate-900 mb-4">Projects Overview</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={projectsWithDatasets}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip contentStyle={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }} />
                  <Legend />
                  <Bar dataKey="datasets" fill="#8b5cf6" name="Datasets" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Recent Projects and Datasets */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Folder className="h-4 w-4 text-blue-600" />
                  Recent Projects
                </h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push('/projects')}
                  className="text-blue-600 hover:text-blue-700 text-xs"
                >
                  View all →
                </Button>
              </div>
              {loading ? (
                <p className="text-sm text-slate-500">Loading projects...</p>
              ) : recentProjects.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-sm text-slate-500 mb-4">No projects yet.</p>
                  <Button onClick={() => router.push('/projects')} className="bg-blue-600 hover:bg-blue-700">
                    Create Project
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentProjects.map((project) => (
                    <div key={project.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                      <div>
                        <p className="text-sm font-medium text-slate-900">{project.name}</p>
                        <p className="text-xs text-slate-500">
                          {project.dataset_count} {project.dataset_count === 1 ? 'dataset' : 'datasets'}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/projects/${project.id}`)}
                        className="text-xs"
                      >
                        Open
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            <Card className="p-6 border border-slate-100">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-purple-600" />
                  Recent Datasets
                </h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push('/upload')}
                  className="text-blue-600 hover:text-blue-700 text-xs"
                >
                  Upload new →
                </Button>
              </div>
              {loading ? (
                <p className="text-sm text-slate-500">Loading datasets...</p>
              ) : recentDatasets.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-sm text-slate-500 mb-4">No datasets uploaded yet.</p>
                  <Button onClick={() => router.push('/upload')} className="bg-blue-600 hover:bg-blue-700">
                    Upload Dataset
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentDatasets.map((dataset) => (
                    <div key={dataset.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900 truncate">{dataset.filename}</p>
                        <p className="text-xs text-slate-500">
                          {new Date(dataset.upload_date).toLocaleDateString()} · {Math.round(dataset.size_bytes / 1024)} KB
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`text-xs font-semibold px-2 py-1 rounded ${
                          typeof dataset.health_score === 'number' && dataset.health_score >= 70
                            ? 'bg-green-100 text-green-700'
                            : 'bg-orange-100 text-orange-700'
                        }`}>
                          {typeof dataset.health_score === 'number' ? `${Math.round(dataset.health_score)}%` : '—'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
