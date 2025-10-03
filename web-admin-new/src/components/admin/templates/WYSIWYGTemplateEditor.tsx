import React, { useState, useEffect, useRef } from 'react';
import { Editor } from '@tinymce/tinymce-react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Save as SaveIcon,
  Preview as PreviewIcon,
  Publish as PublishIcon,
  History as HistoryIcon,
  Compare as CompareIcon,
  ExpandMore as ExpandMoreIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  PictureAsPdf as PdfIcon,
  Image as ImageIcon,
  Code as CodeIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

import { templateService } from '../../../services/templateService';
import { PreviewDialog } from './PreviewDialog';
import { VersionHistoryDialog } from './VersionHistoryDialog';
import { CompareVersionsDialog } from './CompareVersionsDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`wysiwyg-tabpanel-${index}`}
      aria-labelledby={`wysiwyg-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface WYSIWYGTemplateEditorProps {
  templateId: number;
  versionId?: number;
  onSave?: (version: any) => void;
  onPublish?: (version: any) => void;
}

export const WYSIWYGTemplateEditor: React.FC<WYSIWYGTemplateEditorProps> = ({
  templateId,
  versionId,
  onSave,
  onPublish
}) => {
  // State management
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [editorConfig, setEditorConfig] = useState(null);
  
  // Template data
  const [templateVersion, setTemplateVersion] = useState(null);
  const [htmlContent, setHtmlContent] = useState('');
  const [cssStyles, setCssStyles] = useState('');
  const [editorContent, setEditorContent] = useState({});
  const [metadata, setMetadata] = useState({
    title: '',
    description: '',
    page_size: 'A4',
    orientation: 'portrait',
    include_qr_code: true,
    qr_code_position: 'top_right',
    include_logo: true,
    logo_position: 'top_left'
  });
  
  // Dialogs
  const [previewDialog, setPreviewDialog] = useState(false);
  const [historyDialog, setHistoryDialog] = useState(false);
  const [compareDialog, setCompareDialog] = useState(false);
  const [publishDialog, setPublishDialog] = useState(false);
  
  // Messages
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'info' });
  
  // Refs
  const editorRef = useRef(null);
  
  useEffect(() => {
    loadEditorConfig();
    if (versionId) {
      loadTemplateVersion();
    }
  }, [templateId, versionId]);
  
  const loadEditorConfig = async () => {
    try {
      const response = await templateService.getEditorConfig();
      setEditorConfig(response.data.editor_config);
    } catch (error) {
      console.error('Failed to load editor config:', error);
      showAlert('Nem sikerült betölteni a szerkesztő konfigurációt', 'error');
    }
  };
  
  const loadTemplateVersion = async () => {
    if (!versionId) return;
    
    setLoading(true);
    try {
      const response = await templateService.getTemplateVersion(versionId);
      const version = response.data.version;
      
      setTemplateVersion(version);
      setHtmlContent(version.html_template || '');
      setCssStyles(version.css_styles || '');
      setEditorContent(version.editor_content || {});
      setMetadata({
        title: version.title || '',
        description: version.description || '',
        page_size: version.page_size || 'A4',
        orientation: version.orientation || 'portrait',
        include_qr_code: version.include_qr_code ?? true,
        qr_code_position: version.qr_code_position || 'top_right',
        include_logo: version.include_logo ?? true,
        logo_position: version.logo_position || 'top_left'
      });
      
    } catch (error) {
      console.error('Failed to load template version:', error);
      showAlert('Nem sikerült betölteni a sablon verziót', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSave = async (versionType = 'minor') => {
    setSaving(true);
    try {
      const requestData = {
        html_content: htmlContent,
        css_styles: cssStyles,
        editor_content: editorContent,
        version_type: versionType,
        metadata: metadata
      };
      
      let response;
      if (versionId && templateVersion?.status === 'draft') {
        // Update existing draft
        response = await templateService.updateTemplateVersion(versionId, requestData);
      } else {
        // Create new version
        response = await templateService.createTemplateVersion(templateId, requestData);
      }
      
      const newVersion = response.data.version;
      setTemplateVersion(newVersion);
      
      showAlert('Sablon verzió sikeresen mentve', 'success');
      
      if (onSave) {
        onSave(newVersion);
      }
      
    } catch (error) {
      console.error('Failed to save template version:', error);
      showAlert('Nem sikerült menteni a sablon verziót', 'error');
    } finally {
      setSaving(false);
    }
  };
  
  const handlePublish = async () => {
    if (!templateVersion) return;
    
    try {
      const response = await templateService.publishTemplateVersion(templateVersion.id, {
        approval_notes: 'Published from WYSIWYG editor'
      });
      
      const publishedVersion = response.data.version;
      setTemplateVersion(publishedVersion);
      
      showAlert('Sablon verzió sikeresen publikálva', 'success');
      setPublishDialog(false);
      
      if (onPublish) {
        onPublish(publishedVersion);
      }
      
    } catch (error) {
      console.error('Failed to publish template version:', error);
      showAlert('Nem sikerült publikálni a sablon verziót', 'error');
    }
  };
  
  const handlePreview = async () => {
    if (!templateVersion) {
      showAlert('Mentse el a sablont az előnézet megtekintéséhez', 'warning');
      return;
    }
    
    setPreviewDialog(true);
  };
  
  const handleEditorChange = (content, editor) => {
    setHtmlContent(content);
    
    // Save editor state
    if (editor) {
      setEditorContent({
        content: content,
        selection: editor.selection.getBookmark(),
        undoManager: editor.undoManager.data
      });
    }
  };
  
  const handleMetadataChange = (field, value) => {
    setMetadata(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const showAlert = (message, severity = 'info') => {
    setAlert({
      open: true,
      message,
      severity
    });
  };
  
  const closeAlert = () => {
    setAlert(prev => ({ ...prev, open: false }));
  };
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      {/* Alert Snackbar */}
      {alert.open && (
        <Alert 
          severity={alert.severity} 
          onClose={closeAlert}
          sx={{ mb: 2 }}
        >
          {alert.message}
        </Alert>
      )}
      
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="between" alignItems="center">
          <Typography variant="h5">
            WYSIWYG Sablon Szerkesztő
            {templateVersion && (
              <Chip 
                label={`v${templateVersion.version_number}`} 
                color={templateVersion.status === 'published' ? 'success' : 'default'}
                sx={{ ml: 2 }}
              />
            )}
          </Typography>
          
          <Box display="flex" gap={1}>
            <Button
              startIcon={<PreviewIcon />}
              onClick={handlePreview}
              disabled={!templateVersion}
            >
              Előnézet
            </Button>
            
            <Button
              startIcon={<HistoryIcon />}
              onClick={() => setHistoryDialog(true)}
            >
              Változások
            </Button>
            
            <Button
              startIcon={<SaveIcon />}
              onClick={() => handleSave()}
              disabled={saving}
              variant="contained"
            >
              {saving ? <CircularProgress size={20} /> : 'Mentés'}
            </Button>
            
            {templateVersion?.status === 'draft' && (
              <Button
                startIcon={<PublishIcon />}
                onClick={() => setPublishDialog(true)}
                variant="contained"
                color="success"
              >
                Publikálás
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
      
      {/* Main Editor */}
      <Paper sx={{ p: 0 }}>
        <Tabs 
          value={currentTab} 
          onChange={(e, newValue) => setCurrentTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="WYSIWYG Szerkesztő" />
          <Tab label="CSS Stílusok" />
          <Tab label="Beállítások" />
          <Tab label="Változók" />
        </Tabs>
        
        {/* WYSIWYG Editor Tab */}
        <TabPanel value={currentTab} index={0}>
          {editorConfig && (
            <Editor
              ref={editorRef}
              apiKey="your-tinymce-api-key" // Replace with your TinyMCE API key
              value={htmlContent}
              init={{
                ...editorConfig.tinymce,
                setup: (editor) => {
                  editor.on('change', () => {
                    const content = editor.getContent();
                    handleEditorChange(content, editor);
                  });
                }
              }}
              onEditorChange={(content, editor) => {
                handleEditorChange(content, editor);
              }}
            />
          )}
          
          {/* Available Variables Helper */}
          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Elérhető változók</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {editorConfig?.available_variables && Object.entries(editorConfig.available_variables).map(([category, variables]) => (
                  <Grid item xs={12} md={6} key={category}>
                    <Typography variant="subtitle2" gutterBottom>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {variables.map((variable) => (
                        <Chip
                          key={variable}
                          label={`{{${variable}}}`}
                          size="small"
                          onClick={() => {
                            if (editorRef.current) {
                              const editor = editorRef.current.getEditor();
                              editor.insertContent(`{{${variable}}}`);
                            }
                          }}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        </TabPanel>
        
        {/* CSS Styles Tab */}
        <TabPanel value={currentTab} index={1}>
          <TextField
            multiline
            rows={20}
            fullWidth
            value={cssStyles}
            onChange={(e) => setCssStyles(e.target.value)}
            placeholder="/* CSS stílusok a sablonhoz */
.document-header {
  text-align: center;
  margin-bottom: 20px;
}

.document-content {
  line-height: 1.6;
}

/* További stílusok... */"
            variant="outlined"
            sx={{ fontFamily: 'monospace' }}
          />
          
          {/* CSS Classes Helper */}
          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Előre definiált CSS osztályok</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {editorConfig?.css_classes?.map((className) => (
                  <Chip
                    key={className}
                    label={`.${className}`}
                    size="small"
                    onClick={() => {
                      const newCss = cssStyles + `\n.${className} {\n  /* Stílusok */\n}\n`;
                      setCssStyles(newCss);
                    }}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>
        </TabPanel>
        
        {/* Settings Tab */}
        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Sablon címe"
                value={metadata.title}
                onChange={(e) => handleMetadataChange('title', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Oldal méret</InputLabel>
                <Select
                  value={metadata.page_size}
                  onChange={(e) => handleMetadataChange('page_size', e.target.value)}
                >
                  <MenuItem value="A4">A4</MenuItem>
                  <MenuItem value="A3">A3</MenuItem>
                  <MenuItem value="Letter">Letter</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Leírás"
                value={metadata.description}
                onChange={(e) => handleMetadataChange('description', e.target.value)}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Orientáció</InputLabel>
                <Select
                  value={metadata.orientation}
                  onChange={(e) => handleMetadataChange('orientation', e.target.value)}
                >
                  <MenuItem value="portrait">Álló</MenuItem>
                  <MenuItem value="landscape">Fekvő</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>QR kód pozíció</InputLabel>
                <Select
                  value={metadata.qr_code_position}
                  onChange={(e) => handleMetadataChange('qr_code_position', e.target.value)}
                  disabled={!metadata.include_qr_code}
                >
                  <MenuItem value="top_left">Bal felső</MenuItem>
                  <MenuItem value="top_right">Jobb felső</MenuItem>
                  <MenuItem value="bottom_left">Bal alsó</MenuItem>
                  <MenuItem value="bottom_right">Jobb alsó</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Variables Tab */}
        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Sablon változók dokumentáció
          </Typography>
          
          <List>
            {editorConfig?.available_variables && Object.entries(editorConfig.available_variables).map(([category, variables]) => (
              <div key={category}>
                <ListItem>
                  <ListItemIcon>
                    <CodeIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={category.charAt(0).toUpperCase() + category.slice(1)}
                    secondary={`${variables.length} változó elérhető`}
                  />
                </ListItem>
                {variables.map((variable) => (
                  <ListItem key={variable} sx={{ pl: 4 }}>
                    <ListItemText
                      primary={`{{${variable}}}`}
                      secondary={getVariableDescription(variable)}
                    />
                  </ListItem>
                ))}
                <Divider />
              </div>
            ))}
          </List>
        </TabPanel>
      </Paper>
      
      {/* Preview Dialog */}
      {previewDialog && templateVersion && (
        <PreviewDialog
          open={previewDialog}
          onClose={() => setPreviewDialog(false)}
          versionId={templateVersion.id}
        />
      )}
      
      {/* Version History Dialog */}
      {historyDialog && (
        <VersionHistoryDialog
          open={historyDialog}
          onClose={() => setHistoryDialog(false)}
          templateId={templateId}
          onVersionSelect={(version) => {
            // Navigate to selected version
            window.location.href = `/admin/templates/${templateId}/versions/${version.id}`;
          }}
        />
      )}
      
      {/* Compare Versions Dialog */}
      {compareDialog && (
        <CompareVersionsDialog
          open={compareDialog}
          onClose={() => setCompareDialog(false)}
          templateId={templateId}
        />
      )}
      
      {/* Publish Confirmation Dialog */}
      <Dialog open={publishDialog} onClose={() => setPublishDialog(false)}>
        <DialogTitle>Sablon verzió publikálása</DialogTitle>
        <DialogContent>
          <Typography>
            Biztosan publikálni szeretné ezt a sablon verziót? 
            A publikálás után a verzió aktív lesz és használható dokumentum generáláshoz.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPublishDialog(false)}>Mégse</Button>
          <Button onClick={handlePublish} variant="contained" color="success">
            Publikálás
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Helper function for variable descriptions
function getVariableDescription(variable: string): string {
  const descriptions = {
    'document_number': 'A dokumentum egyedi azonosítója',
    'document_title': 'A dokumentum címe',
    'generation.date': 'A dokumentum generálás dátuma',
    'generation.generated_by': 'A dokumentumot generáló felhasználó',
    'organization.name': 'A szervezet neve',
    'organization.address': 'A szervezet címe',
    'gate.id': 'A kapu azonosítója',
    'gate.name': 'A kapu neve',
    'inspector.name': 'Az ellenőr neve',
    'inspection.date': 'Az ellenőrzés dátuma',
    'inspection.result': 'Az ellenőrzés eredménye'
  };
  
  return descriptions[variable] || 'Sablon változó';
}

export default WYSIWYGTemplateEditor;