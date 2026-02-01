import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Box,
  Paper,
  Stack,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Alert
} from '@mui/material';
import axios from 'axios';
import type { RAGRequest, RAGResponse, ContextChunk } from './types';

function App() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(8);
  const [useRerank, setUseRerank] = useState(true);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const request: RAGRequest = {
      query,
      top_k: topK,
      use_rerank: useRerank,
    };

    try {
      // Use the environment variable if available, otherwise default to relative path
      // In development, Vite will proxy requests or you can set VITE_API_BASE_URL
      // In production (single container), relative path works best.
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const res = await axios.post<RAGResponse>(`${baseUrl}/rag`, request);
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch response from the API. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        RAG Console
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            <TextField
              label="Query"
              variant="outlined"
              fullWidth
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question here..."
              required
            />

            <Stack direction="row" spacing={3} alignItems="center">
              <TextField
                label="Top K"
                type="number"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value) || 1)}
                inputProps={{ min: 1, max: 20 }}
                sx={{ width: 100 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={useRerank}
                    onChange={(e) => setUseRerank(e.target.checked)}
                    color="primary"
                  />
                }
                label="Use Rerank"
              />
            </Stack>

            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || !query.trim()}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Query'}
            </Button>
          </Stack>
        </form>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {response && (
        <Box>
          <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: '#f5f5f5' }}>
            <Typography variant="h5" gutterBottom>
              Synthesized Answer
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {response.synthesized_answer}
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={2}>
                <Typography variant="caption" color="text.secondary">
                    Confidence: {(response.confidence_score * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                    Citations: {response.citations.join(', ')}
                </Typography>
            </Stack>
          </Paper>

          <Typography variant="h5" gutterBottom>
            Retrieved Contexts
          </Typography>
          <Stack spacing={2}>
            {response.retrieved_contexts.map((ctx: ContextChunk) => (
              <Card key={ctx.doc_id} variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Document ID: {ctx.doc_id} {ctx.section && `- ${ctx.section}`} (Score: {ctx.score.toFixed(4)})
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {ctx.text}
                  </Typography>
                  {ctx.meta && Object.keys(ctx.meta).length > 0 && (
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                          Meta: {JSON.stringify(ctx.meta)}
                      </Typography>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      )}
    </Container>
  );
}

export default App;
