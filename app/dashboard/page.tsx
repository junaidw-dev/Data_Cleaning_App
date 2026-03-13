'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';
import { Plus, Folder, Upload, LogOut, Settings } from 'lucide-react';

interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  dataset_count: number;
}

export default function DashboardPage() {
  const { user, logout, token } = useAuth();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  const fetchProjects = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [token]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newProjectName.trim()) return;

    setCreateLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newProjectName,
          description: newProjectDesc,
        }),
      });

      if (response.ok) {
        const newProject = await response.json();
        setProjects([newProject, ...projects]);
        setNewProjectName('');
        setNewProjectDesc('');
        setShowNewProject(false);
      }
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-50">
        {/* Header */}
        <header className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
              <p className="text-slate-600 text-sm">Welcome, {user?.full_name}</p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
              <Button variant="destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-12">
          {/* Stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="p-6">
              <div className="text-4xl font-bold text-blue-600 mb-2">{projects.length}</div>
              <p className="text-slate-600">Projects</p>
            </Card>
            <Card className="p-6">
              <div className="text-4xl font-bold text-green-600 mb-2">
                {projects.reduce((sum, p) => sum + p.dataset_count, 0)}
              </div>
              <p className="text-slate-600">Total Datasets</p>
            </Card>
            <Card className="p-6">
              <div className="text-4xl font-bold text-purple-600 mb-2">{user?.subscription_tier.toUpperCase()}</div>
              <p className="text-slate-600">Plan</p>
            </Card>
          </div>

          {/* Create Project Section */}
          {!showNewProject ? (
            <Button
              onClick={() => setShowNewProject(true)}
              className="bg-blue-600 hover:bg-blue-700 mb-8"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          ) : (
            <Card className="p-6 mb-8">
              <h2 className="text-lg font-semibold mb-4">Create New Project</h2>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <Label htmlFor="projectName">Project Name</Label>
                  <Input
                    id="projectName"
                    placeholder="e.g., Q1 Sales Analysis"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    disabled={createLoading}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="projectDesc">Description (Optional)</Label>
                  <Input
                    id="projectDesc"
                    placeholder="Describe your project..."
                    value={newProjectDesc}
                    onChange={(e) => setNewProjectDesc(e.target.value)}
                    disabled={createLoading}
                  />
                </div>
                <div className="flex gap-3">
                  <Button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700"
                    disabled={createLoading}
                  >
                    {createLoading ? 'Creating...' : 'Create Project'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowNewProject(false);
                      setNewProjectName('');
                      setNewProjectDesc('');
                    }}
                    disabled={createLoading}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Projects Grid */}
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-6">Your Projects</h2>
            {loading ? (
              <div className="text-center py-12">
                <p className="text-slate-600">Loading projects...</p>
              </div>
            ) : projects.length === 0 ? (
              <Card className="p-12 text-center">
                <Folder className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No projects yet</h3>
                <p className="text-slate-600 mb-4">Create your first project to get started</p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <Card
                    key={project.id}
                    className="p-6 hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => router.push(`/projects/${project.id}`)}
                  >
                    <div className="flex items-start gap-3 mb-4">
                      <Folder className="h-8 w-8 text-blue-600 flex-shrink-0" />
                      <div>
                        <h3 className="font-semibold text-slate-900">{project.name}</h3>
                        {project.description && (
                          <p className="text-sm text-slate-600 mt-1">{project.description}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex justify-between items-end">
                      <div className="text-sm text-slate-600">
                        <p className="font-medium">{project.dataset_count} datasets</p>
                        <p className="text-xs">
                          Created {new Date(project.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/projects/${project.id}`);
                        }}
                      >
                        <Upload className="h-4 w-4 mr-1" />
                        Upload
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
