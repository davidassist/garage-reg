// Template Service for WYSIWYG Template Management
import axios from 'axios';

const API_BASE_URL = '/api/admin/wysiwyg-templates';

export class TemplateService {
  async getEditorConfig() {
    return axios.get(`${API_BASE_URL}/editor-config`);
  }

  async createTemplateVersion(templateId: number, data: any) {
    return axios.post(`${API_BASE_URL}/templates/${templateId}/versions`, data);
  }

  async updateTemplateVersion(versionId: number, data: any) {
    return axios.put(`${API_BASE_URL}/versions/${versionId}`, data);
  }

  async getTemplateVersion(versionId: number) {
    return axios.get(`${API_BASE_URL}/versions/${versionId}`);
  }

  async getTemplateVersions(templateId: number, includeDrafts = true, limit = 50) {
    return axios.get(`${API_BASE_URL}/templates/${templateId}/versions`, {
      params: { include_drafts: includeDrafts, limit }
    });
  }

  async publishTemplateVersion(versionId: number, data: any) {
    return axios.post(`${API_BASE_URL}/versions/${versionId}/publish`, data);
  }

  async createPreviewSession(versionId: number, data: any) {
    return axios.post(`${API_BASE_URL}/versions/${versionId}/preview`, data);
  }

  async getPreviewStatus(sessionToken: string) {
    return axios.get(`${API_BASE_URL}/preview/${sessionToken}/status`);
  }

  async getPreviewHtml(sessionToken: string) {
    return `${API_BASE_URL}/preview/${sessionToken}/html`;
  }

  async getPreviewPdf(sessionToken: string) {
    return `${API_BASE_URL}/preview/${sessionToken}/pdf`;
  }

  async getPreviewImage(sessionToken: string) {
    return `${API_BASE_URL}/preview/${sessionToken}/image`;
  }

  async getTemplateChangelog(templateId: number, limit = 100) {
    return axios.get(`${API_BASE_URL}/templates/${templateId}/changelog`, {
      params: { limit }
    });
  }

  async compareVersions(versionId1: number, versionId2: number) {
    return axios.get(`${API_BASE_URL}/versions/${versionId1}/compare/${versionId2}`);
  }

  async uploadEditorAsset(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_BASE_URL}/upload/editor-asset`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
}

export const templateService = new TemplateService();