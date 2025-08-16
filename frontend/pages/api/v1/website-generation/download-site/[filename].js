export default async function handler(req, res) {
  const { filename } = req.query;

  if (!filename) {
    return res.status(400).json({ error: 'Filename is required' });
  }

  try {
    // For demo purposes, redirect to the demo page
    // In production, this would serve the actual generated HTML file
    const demoUrl = `https://agentic-ai-webtrials.vercel.app/demo/${filename}`;
    
    res.redirect(demoUrl);
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}
