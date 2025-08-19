const fs = require('fs');

class SerpApiPageSpeedSummary {
  constructor() {
    this.resultsFile = './serpapi-pagespeed-results-2025-08-18.json';
    this.results = null;
  }

  // Load the PageSpeed results
  loadResults() {
    try {
      if (!fs.existsSync(this.resultsFile)) {
        throw new Error(`Results file not found: ${this.resultsFile}`);
      }
      
      const data = fs.readFileSync(this.resultsFile, 'utf8');
      this.results = JSON.parse(data);
      
      console.log(`📊 Loaded PageSpeed results for ${this.results.results.length} analyses`);
      console.log(`🔍 Query: "${this.results.serpApiQuery.query}" in ${this.results.serpApiQuery.location}`);
      console.log(`⏰ Analysis completed: ${new Date(this.results.analysisTimestamp).toLocaleString()}`);
      console.log('='.repeat(80));
      
      return this.results;
    } catch (error) {
      console.error('❌ Error loading results:', error.message);
      throw error;
    }
  }

  // Group results by website
  groupByWebsite() {
    const websites = new Map();
    
    this.results.results.forEach(result => {
      const websiteKey = result.website.website;
      
      if (!websites.has(websiteKey)) {
        websites.set(websiteKey, {
          ...result.website,
          mobile: null,
          desktop: null
        });
      }
      
      if (result.strategy === 'mobile') {
        websites.get(websiteKey).mobile = result;
      } else if (result.strategy === 'desktop') {
        websites.get(websiteKey).desktop = result;
      }
    });
    
    return Array.from(websites.values());
  }

  // Calculate average scores
  calculateAverageScores(website) {
    const scores = ['performance', 'accessibility', 'bestPractices', 'seo'];
    const averages = {};
    
    scores.forEach(scoreType => {
      const mobileScore = website.mobile?.scores[scoreType] || 0;
      const desktopScore = website.desktop?.scores[scoreType] || 0;
      
      if (mobileScore && desktopScore) {
        averages[scoreType] = Math.round((mobileScore + desktopScore) / 2);
      } else if (mobileScore) {
        averages[scoreType] = mobileScore;
      } else if (desktopScore) {
        averages[scoreType] = desktopScore;
      } else {
        averages[scoreType] = 0;
      }
    });
    
    return averages;
  }

  // Rank websites by performance
  rankWebsites(websites) {
    return websites.map(website => {
      const averages = this.calculateAverageScores(website);
      const overallScore = Math.round(
        Object.values(averages).reduce((sum, score) => sum + score, 0) / 4
      );
      
      return {
        ...website,
        averageScores: averages,
        overallScore: overallScore
      };
    }).sort((a, b) => b.overallScore - a.overallScore);
  }

  // Print website summary
  printWebsiteSummary(website, rank) {
    const averages = website.averageScores;
    
    console.log(`\n🏆 #${rank} - ${website.name}`);
    console.log(`🌐 ${website.website}`);
    console.log(`📍 ${website.address}`);
    console.log(`⭐ Rating: ${website.rating}/5 (${website.reviews} reviews)`);
    console.log(`📊 Overall Score: ${website.overallScore}/100`);
    
    console.log('\n📱 Mobile Performance:');
    if (website.mobile) {
      console.log(`   Performance: ${website.mobile.scores.performance}/100`);
      console.log(`   Accessibility: ${website.mobile.scores.accessibility}/100`);
      console.log(`   Best Practices: ${website.mobile.scores.bestPractices}/100`);
      console.log(`   SEO: ${website.mobile.scores.seo}/100`);
    } else {
      console.log('   ❌ No mobile data available');
    }
    
    console.log('\n💻 Desktop Performance:');
    if (website.desktop) {
      console.log(`   Performance: ${website.desktop.scores.performance}/100`);
      console.log(`   Accessibility: ${website.desktop.scores.accessibility}/100`);
      console.log(`   Best Practices: ${website.desktop.scores.bestPractices}/100`);
      console.log(`   SEO: ${website.desktop.scores.seo}/100`);
    } else {
      console.log('   ❌ No desktop data available');
    }
    
    console.log('\n📈 Average Scores:');
    console.log(`   Performance: ${averages.performance}/100`);
    console.log(`   Accessibility: ${averages.accessibility}/100`);
    console.log(`   Best Practices: ${averages.bestPractices}/100`);
    console.log(`   SEO: ${averages.seo}/100`);
    
    console.log('─'.repeat(80));
  }

  // Print performance insights
  printPerformanceInsights(rankedWebsites) {
    console.log('\n🔍 PERFORMANCE INSIGHTS');
    console.log('='.repeat(80));
    
    // Best performers
    const bestPerformer = rankedWebsites[0];
    console.log(`🥇 Best Overall: ${bestPerformer.name} (${bestPerformer.overallScore}/100)`);
    
    // Mobile vs Desktop comparison
    const mobileScores = rankedWebsites
      .filter(w => w.mobile)
      .map(w => w.mobile.scores.performance);
    const desktopScores = rankedWebsites
      .filter(w => w.desktop)
      .map(w => w.desktop.scores.performance);
    
    const avgMobilePerformance = Math.round(
      mobileScores.reduce((sum, score) => sum + score, 0) / mobileScores.length
    );
    const avgDesktopPerformance = Math.round(
      desktopScores.reduce((sum, score) => sum + score, 0) / desktopScores.length
    );
    
    console.log(`📱 Average Mobile Performance: ${avgMobilePerformance}/100`);
    console.log(`💻 Average Desktop Performance: ${avgDesktopPerformance}/100`);
    
    // Performance distribution
    const excellent = rankedWebsites.filter(w => w.overallScore >= 90).length;
    const good = rankedWebsites.filter(w => w.overallScore >= 70 && w.overallScore < 90).length;
    const needsImprovement = rankedWebsites.filter(w => w.overallScore < 70).length;
    
    console.log(`\n📊 Performance Distribution:`);
    console.log(`   🟢 Excellent (90+): ${excellent} websites`);
    console.log(`   🟡 Good (70-89): ${good} websites`);
    console.log(`   🔴 Needs Improvement (<70): ${needsImprovement} websites`);
    
    // Common optimization opportunities
    console.log(`\n💡 Common Optimization Opportunities:`);
    const allOpportunities = [];
    rankedWebsites.forEach(website => {
      if (website.mobile?.opportunities) {
        allOpportunities.push(...website.mobile.opportunities.map(o => o.title));
      }
      if (website.desktop?.opportunities) {
        allOpportunities.push(...website.desktop.opportunities.map(o => o.title));
      }
    });
    
    const opportunityCounts = {};
    allOpportunities.forEach(opp => {
      opportunityCounts[opp] = (opportunityCounts[opp] || 0) + 1;
    });
    
    const topOpportunities = Object.entries(opportunityCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5);
    
    topOpportunities.forEach(([opportunity, count], index) => {
      console.log(`   ${index + 1}. ${opportunity} (${count} occurrences)`);
    });
  }

  // Generate summary report
  generateSummary() {
    try {
      console.log('📋 Generating SERP API PageSpeed Summary Report...\n');
      
      // Load results
      this.loadResults();
      
      // Group and rank websites
      const websites = this.groupByWebsite();
      const rankedWebsites = this.rankWebsites(websites);
      
      // Print rankings
      console.log('\n🏆 WEBSITE RANKINGS BY OVERALL PERFORMANCE');
      console.log('='.repeat(80));
      
      rankedWebsites.forEach((website, index) => {
        this.printWebsiteSummary(website, index + 1);
      });
      
      // Print insights
      this.printPerformanceInsights(rankedWebsites);
      
      // Save summary to file
      const summaryFilename = `serpapi-pagespeed-summary-${new Date().toISOString().split('T')[0]}.json`;
      const summary = {
        generatedAt: new Date().toISOString(),
        query: this.results.serpApiQuery,
        totalWebsites: rankedWebsites.length,
        rankings: rankedWebsites.map((website, index) => ({
          rank: index + 1,
          name: website.name,
          website: website.website,
          overallScore: website.overallScore,
          averageScores: website.averageScores,
          rating: website.rating,
          reviews: website.reviews
        })),
        insights: {
          bestPerformer: rankedWebsites[0]?.name,
          bestScore: rankedWebsites[0]?.overallScore,
          averageMobilePerformance: Math.round(
            rankedWebsites
              .filter(w => w.mobile)
              .reduce((sum, w) => sum + w.mobile.scores.performance, 0) / 
            rankedWebsites.filter(w => w.mobile).length
          ),
          averageDesktopPerformance: Math.round(
            rankedWebsites
              .filter(w => w.desktop)
              .reduce((sum, w) => sum + w.desktop.scores.performance, 0) / 
            rankedWebsites.filter(w => w.desktop).length
          )
        }
      };
      
      fs.writeFileSync(summaryFilename, JSON.stringify(summary, null, 2));
      console.log(`\n💾 Summary report saved to ${summaryFilename}`);
      
    } catch (error) {
      console.error('❌ Error generating summary:', error.message);
      process.exit(1);
    }
  }
}

// Main execution function
async function main() {
  const summary = new SerpApiPageSpeedSummary();
  summary.generateSummary();
}

// Run the application if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = SerpApiPageSpeedSummary;
