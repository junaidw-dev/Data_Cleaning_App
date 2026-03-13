'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useProjects, Project } from '@/hooks/useDataApi';
import { ProtectedRoute } from '@/app/components/ProtectedRoute';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Folder, Plus, Upload } from 'lucide-react';

export default function ProjectsPage() {
  const router = useRouter();
  const { listProjects, createProject, loading } = useProjects();
  const [projects, setProjects] = useState<Project[]>([]);
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    setCreateLoading(true);
    try {
      const project = await createProject(newProjectName, newProjectDesc || undefined);
      setProjects([project, ...projects]);
      setNewProjectName('');
      setNewProjectDesc('');
      setShowNewProject(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Projects</h1>
              <p className="text-slate-600">Organize datasets and analysis by project</p>
            </div>
            {!showNewProject && (
              <Button onClick={() => setShowNewProject(true)} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            )}
          </div>

          {error && (
            <Card className="p-4 mb-6 border border-red-200 bg-red-50 text-red-700">
              {error}
            </Card>
          )}

          {showNewProject && (
            <Card className="p-6 mb-8">
              <h2 className="text-lg font-semibold mb-4">Create New Project</h2>
              <form onSubmit={handleCreateProject} className="space-y-4">
                <div>
                  <Label htmlFor="projectName">Project Name</Label>
                  <Input
                    id="projectName"
                    placeholder="e.g., Q2 Customer Churn"
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
                    placeholder="Describe your analysis goal"
                    value={newProjectDesc}
                    onChange={(e) => setNewProjectDesc(e.target.value)}
                    disabled={createLoading}
                  />
                </div>
                <div className="flex gap-3">
                  <Button type="submit" className="bg-blue-600 hover:bg-blue-700" disabled={createLoading}>
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

          {loading ? (
            <Card className="p-8 text-center text-slate-600">Loading projects...</Card>
          ) : projects.length === 0 ? (
            <Card className="p-8 text-center">
              <Folder className="h-12 w-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-600 mb-4">No projects yet. Create your first project.</p>
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
                      <p className="text-xs">Created {new Date(project.created_at).toLocaleDateString()}</p>
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
                      Open
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
