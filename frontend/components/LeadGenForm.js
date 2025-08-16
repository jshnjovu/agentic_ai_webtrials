import { useState } from "react";
import {
  Input,
  Button,
  Layout,
  Typography,
  Form,
  Table,
  Spin,
  Alert,
  Row,
  Col,
} from "antd";

const { Header, Content } = Layout;
const { Title } = Typography;

export default function LeadGenForm() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [generatedSites, setGeneratedSites] = useState([]);

  const columns = [
    {
      title: "Business Name",
      dataIndex: "business_name",
      key: "business_name",
    },
    {
      title: "Website",
      dataIndex: "website",
      key: "website",
      render: (text) => (
        <a href={text} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      ),
    },
    {
      title: "Score",
      dataIndex: "score_overall",
      key: "score_overall",
      render: (score) => (
        <span style={{ 
          color: score < 70 ? '#ff4d4f' : score < 85 ? '#faad14' : '#52c41a',
          fontWeight: 'bold'
        }}>
          {score}/100
        </span>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          disabled={record.score_overall >= 70}
          onClick={() => handleGenerateWebsite(record)}
          loading={record.generating}
        >
          {record.score_overall >= 70 ? "Good Score" : "Generate Website"}
        </Button>
      ),
    },
  ];

  const onFinish = async (values) => {
    setLoading(true);
    setResults([]);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/leadgen-agent/discover-businesses`,
        {
          method: "POST",
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            location: values.location,
            niche: values.niche
          })
        }
      );

      if (!response.ok) {
        throw new Error("Failed to discover businesses");
      }

      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateWebsite = async (business) => {
    // Mark this business as generating
    setResults(prev => prev.map(item => 
      item.business_name === business.business_name 
        ? { ...item, generating: true }
        : item
    ));

    try {
      const response = await fetch('/api/v1/website-generation/generate-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          business_name: business.business_name,
          location: business.location || 'Unknown',
          niche: business.niche || 'Business',
          website: business.website,
          address: business.address,
          phone: business.phone,
          score_overall: business.score_overall,
          score_perf: business.score_perf || 0,
          score_access: business.score_access || 0,
          score_seo: business.score_seo || 0,
          score_trust: business.score_trust || 0,
          score_cro: business.score_cro || 0,
          top_issues: business.top_issues || [],
          timestamp: new Date().toISOString(),
          run_id: `run_${Date.now()}`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate website');
      }

      const data = await response.json();
      
      if (data.success) {
        // Add generated site to the list
        setGeneratedSites(prev => [...prev, {
          business_name: business.business_name,
          filename: data.files_generated,
          template_used: data.template_used,
          generated_at: new Date().toISOString()
        }]);
        
        // Show success message
        setError(null);
      } else {
        throw new Error(data.message || 'Website generation failed');
      }
    } catch (error) {
      setError(`Failed to generate website for ${business.business_name}: ${error.message}`);
    } finally {
      // Remove generating state
      setResults(prev => prev.map(item => 
        item.business_name === business.business_name 
          ? { ...item, generating: false }
          : item
      ));
    }
  };

  return (
    <Layout>
      <Header style={{ backgroundColor: "white", borderBottom: "1px solid #f0f0f0" }}>
        <Title level={3} style={{ lineHeight: "64px" }}>
          LeadGen Website Makeover Agent
        </Title>
      </Header>
      <Content style={{ padding: "50px" }}>
        <Row justify="center">
          <Col xs={24} sm={20} md={16} lg={12} xl={10}>
            <Form
              layout="vertical"
              onFinish={onFinish}
              initialValues={{ location: "", niche: "" }}
            >
              <Form.Item
                name="location"
                label="Location"
                rules={[
                  {
                    required: true,
                    message: "Please input the location!",
                  },
                ]}
              >
                <Input placeholder="Enter a location (e.g., city, address, ZIP code)" />
              </Form.Item>
              <Form.Item
                name="niche"
                label="Niche"
                rules={[
                  {
                    required: true,
                    message: "Please input the niche!",
                  },
                ]}
              >
                <Input placeholder="Enter a business niche or category" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block>
                  Run Agent
                </Button>
              </Form.Item>
            </Form>
            {loading && <Spin size="large" />}
            {error && <Alert message={error} type="error" />}
            {results.length > 0 && (
              <Table dataSource={results} columns={columns} rowKey="business_name" />
            )}
            
            {generatedSites.length > 0 && (
              <div style={{ marginTop: '2rem' }}>
                <Title level={4}>Generated Websites</Title>
                <Table 
                  dataSource={generatedSites} 
                  columns={[
                    {
                      title: "Business",
                      dataIndex: "business_name",
                      key: "business_name",
                    },
                    {
                      title: "Template Used",
                      dataIndex: "template_used",
                      key: "template_used",
                      render: (template) => (
                        <span style={{ 
                          textTransform: 'capitalize',
                          color: template === 'restaurant' ? '#ff6b6b' : 
                                 template === 'gym' ? '#e74c3c' : '#667eea'
                        }}>
                          {template}
                        </span>
                      ),
                    },
                    {
                      title: "Generated At",
                      dataIndex: "generated_at",
                      key: "generated_at",
                      render: (date) => new Date(date).toLocaleString(),
                    },
                    {
                      title: "Actions",
                      key: "actions",
                      render: (_, record) => (
                        <Button
                          type="link"
                          onClick={() => window.open(`/api/v1/website-generation/download-site/${record.filename}`, '_blank')}
                        >
                          Download
                        </Button>
                      ),
                    },
                  ]} 
                  rowKey="business_name"
                  size="small"
                />
              </div>
            )}
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}
