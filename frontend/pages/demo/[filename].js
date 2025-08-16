import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { Layout, Typography, Spin, Alert, Button } from 'antd';
import { ArrowLeftOutlined, DownloadOutlined, EyeOutlined } from '@ant-design/icons';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

export default function DemoPage() {
  const router = useRouter();
  const { filename } = router.query;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [demoData, setDemoData] = useState(null);

  useEffect(() => {
    if (filename) {
      loadDemoData(filename);
    }
  }, [filename]);

  const loadDemoData = async (filename) => {
    try {
      setLoading(true);
      // Parse filename to extract business info
      const parts = filename.replace('.html', '').split('_');
      const businessName = parts.slice(0, -2).join(' ').replace(/_/g, ' ');
      const niche = parts[parts.length - 2];
      
      setDemoData({
        business_name: businessName,
        niche: niche,
        filename: filename,
        generated_at: new Date().toLocaleString()
      });
    } catch (error) {
      setError('Failed to load demo data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin size="large" />
        </Content>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px', textAlign: 'center' }}>
          <Alert message={error} type="error" showIcon />
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ backgroundColor: 'white', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
            Generated Website Demo
          </Title>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => router.push('/')}
            type="link"
          >
            Back to Generator
          </Button>
        </div>
      </Header>
      
      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <Title level={2}>🎉 Website Generated Successfully!</Title>
          
          <div style={{ 
            background: '#f6f8fa', 
            padding: '30px', 
            borderRadius: '8px', 
            margin: '30px 0',
            border: '1px solid #e1e4e8'
          }}>
            <Title level={4}>Business Details</Title>
            <Text strong>Name:</Text> {demoData.business_name}<br />
            <Text strong>Niche:</Text> {demoData.niche}<br />
            <Text strong>Generated:</Text> {demoData.generated_at}<br />
            <Text strong>File:</Text> {demoData.filename}
          </div>

          <div style={{ margin: '30px 0' }}>
            <Title level={4}>What's Next?</Title>
            <Text>
              This demo shows that your LeadGen Website Makeover Agent successfully generated a website for {demoData.business_name}. 
              In a full implementation, this would create an actual HTML file with a complete website template.
            </Text>
          </div>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button 
              type="primary" 
              size="large"
              icon={<EyeOutlined />}
              onClick={() => window.open(`/api/v1/website-generation/download-site/${demoData.filename}`, '_blank')}
            >
              View Generated Site
            </Button>
            
            <Button 
              size="large"
              icon={<DownloadOutlined />}
              onClick={() => window.open(`/api/v1/website-generation/download-site/${demoData.filename}`, '_blank')}
            >
              Download Files
            </Button>
          </div>

          <div style={{ marginTop: '40px', padding: '20px', background: '#e6f7ff', borderRadius: '6px' }}>
            <Text type="secondary">
              💡 <strong>Demo Mode:</strong> This is running on Vercel for demonstration purposes. 
              The actual website generation would integrate with your backend services and create real HTML files.
            </Text>
          </div>
        </div>
      </Content>
    </Layout>
  );
}
