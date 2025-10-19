"""
Visualization Service for CFR Agentic AI Application
Creates clean visualizations for cluster analysis and similarity matrices
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from app.models.cfr_database import SessionLocal, Cluster, SectionEmbedding, SubchapterEmbedding, ChapterEmbedding
from app.config import VISUALIZATIONS_DIR


class VisualizationService:
    def __init__(self):
        """Initialize visualization service"""
        self.output_dir = VISUALIZATIONS_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def visualize_clusters_2d(self, clusters: List[Dict[str, Any]], 
                             embeddings: List[List[float]],
                             labels: List[int],
                             level: str,
                             method: str = 'tsne') -> str:
        """
        Create 2D visualization of clusters
        
        Args:
            clusters: List of cluster information
            embeddings: List of embeddings
            labels: Cluster labels for each embedding
            level: Level of analysis (chapter/subchapter/section)
            method: Dimensionality reduction method ('tsne' or 'pca')
            
        Returns:
            Path to saved visualization
        """
        # Convert embeddings to numpy array
        X = np.array(embeddings)
        
        # Reduce to 2D
        if method == 'tsne':
            reducer = TSNE(n_components=2, random_state=42)
            X_2d = reducer.fit_transform(X)
        else:  # pca
            reducer = PCA(n_components=2, random_state=42)
            X_2d = reducer.fit_transform(X)
        
        # Create matplotlib figure
        plt.figure(figsize=(14, 10))
        
        # Get unique labels
        unique_labels = sorted(set(labels))
        colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
        
        # Plot each cluster
        for label, color in zip(unique_labels, colors):
            if label == -1:
                # Noise points in black
                color = 'black'
                marker = 'x'
                label_name = 'Noise'
            else:
                marker = 'o'
                # Find cluster size
                cluster_info = next((c for c in clusters if c['label'] == label), None)
                size = cluster_info['size'] if cluster_info else 0
                label_name = f'Cluster {label} (n={size})'
            
            mask = np.array(labels) == label
            plt.scatter(X_2d[mask, 0], X_2d[mask, 1], 
                       c=[color], marker=marker, s=100,
                       alpha=0.7, label=label_name, edgecolors='black', linewidth=0.5)
        
        plt.title(f'{level.title()} Clusters - {method.upper()} Visualization', fontsize=16, fontweight='bold')
        plt.xlabel(f'{method.upper()} Component 1', fontsize=12)
        plt.ylabel(f'{method.upper()} Component 2', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_clusters_{method}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_clusters_interactive(self, clusters: List[Dict[str, Any]],
                                      embeddings: List[List[float]],
                                      labels: List[int],
                                      items: List[Dict[str, Any]],
                                      level: str) -> str:
        """
        Create interactive 3D visualization of clusters using Plotly
        
        Args:
            clusters: List of cluster information
            embeddings: List of embeddings
            labels: Cluster labels
            items: List of item information
            level: Level of analysis
            
        Returns:
            Path to saved HTML visualization
        """
        # Convert embeddings to numpy array
        X = np.array(embeddings)
        
        # Reduce to 3D using PCA
        pca = PCA(n_components=3, random_state=42)
        X_3d = pca.fit_transform(X)
        
        # Prepare data for plotly
        df_data = {
            'x': X_3d[:, 0],
            'y': X_3d[:, 1],
            'z': X_3d[:, 2],
            'cluster': [f'Cluster {l}' if l != -1 else 'Noise' for l in labels],
            'label': labels
        }
        
        # Add item names
        if level == 'chapter':
            df_data['name'] = [item.get('name', '') for item in items]
        elif level == 'subchapter':
            df_data['name'] = [f"{item.get('chapter_name', '')} - {item.get('name', '')}" for item in items]
        elif level == 'section':
            df_data['name'] = [f"{item.get('section_number', '')}: {item.get('subject', '')[:50]}" for item in items]
        
        # Create 3D scatter plot
        fig = px.scatter_3d(df_data, x='x', y='y', z='z', 
                           color='cluster',
                           hover_data=['name'],
                           title=f'{level.title()} Clusters - Interactive 3D Visualization',
                           labels={'x': 'PC1', 'y': 'PC2', 'z': 'PC3'})
        
        fig.update_traces(marker=dict(size=8, line=dict(width=0.5, color='DarkSlateGrey')))
        fig.update_layout(
            scene=dict(
                xaxis_title='Principal Component 1',
                yaxis_title='Principal Component 2',
                zaxis_title='Principal Component 3'
            ),
            width=1200,
            height=800
        )
        
        # Save HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_clusters_interactive_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath
    
    def visualize_similarity_matrix(self, similarity_matrix: np.ndarray,
                                   labels: List[str],
                                   level: str) -> str:
        """
        Visualize similarity matrix as heatmap
        
        Args:
            similarity_matrix: NxN similarity matrix
            labels: Labels for each item
            level: Level of analysis
            
        Returns:
            Path to saved visualization
        """
        plt.figure(figsize=(16, 14))
        
        # Create heatmap
        sns.heatmap(similarity_matrix, 
                   xticklabels=labels if len(labels) <= 50 else False,
                   yticklabels=labels if len(labels) <= 50 else False,
                   cmap='YlOrRd',
                   vmin=0, vmax=1,
                   cbar_kws={'label': 'Cosine Similarity'},
                   square=True)
        
        plt.title(f'{level.title()} Similarity Matrix', fontsize=16, fontweight='bold')
        plt.xlabel('Items', fontsize=12)
        plt.ylabel('Items', fontsize=12)
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_similarity_matrix_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_cluster_sizes(self, clusters: List[Dict[str, Any]], 
                               level: str) -> str:
        """
        Visualize cluster sizes as bar chart
        
        Args:
            clusters: List of cluster information
            level: Level of analysis
            
        Returns:
            Path to saved visualization
        """
        # Prepare data
        labels = [f"Cluster {c['label']}" for c in clusters]
        sizes = [c['size'] for c in clusters]
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(labels, sizes, color=plt.cm.viridis(np.linspace(0, 1, len(clusters))),
                      edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.title(f'{level.title()} Cluster Sizes', fontsize=16, fontweight='bold')
        plt.xlabel('Cluster', fontsize=12)
        plt.ylabel('Number of Items', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_cluster_sizes_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_similarity_distribution(self, similarities: List[float],
                                         level: str) -> str:
        """
        Visualize distribution of similarity scores
        
        Args:
            similarities: List of similarity scores
            level: Level of analysis
            
        Returns:
            Path to saved visualization
        """
        plt.figure(figsize=(12, 6))
        
        # Create histogram
        plt.hist(similarities, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        
        # Add vertical lines for thresholds
        plt.axvline(x=0.75, color='orange', linestyle='--', linewidth=2, label='Similarity Threshold')
        plt.axvline(x=0.80, color='red', linestyle='--', linewidth=2, label='Overlap Threshold')
        plt.axvline(x=0.85, color='darkred', linestyle='--', linewidth=2, label='Redundancy Threshold')
        
        plt.title(f'{level.title()} Similarity Score Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Similarity Score', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(axis='y', alpha=0.3)
        
        # Save figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_similarity_distribution_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_cluster_report(self, clusters: List[Dict[str, Any]],
                            level: str) -> str:
        """
        Create a comprehensive cluster analysis report
        
        Args:
            clusters: List of cluster information
            level: Level of analysis
            
        Returns:
            Path to saved HTML report
        """
        # Calculate statistics
        total_items = sum(c['size'] for c in clusters)
        num_clusters = len(clusters)
        avg_size = total_items / num_clusters if num_clusters > 0 else 0
        min_size = min(c['size'] for c in clusters) if clusters else 0
        max_size = max(c['size'] for c in clusters) if clusters else 0
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{level.title()} Cluster Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #4CAF50;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #555;
                    margin-top: 30px;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background-color: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #1976d2;
                }}
                .stat-label {{
                    color: #555;
                    margin-top: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{level.title()} Cluster Analysis Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <h2>Summary Statistics</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{num_clusters}</div>
                        <div class="stat-label">Total Clusters</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_items}</div>
                        <div class="stat-label">Total Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{avg_size:.1f}</div>
                        <div class="stat-label">Average Size</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{max_size}</div>
                        <div class="stat-label">Largest Cluster</div>
                    </div>
                </div>
                
                <h2>Cluster Details</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Cluster ID</th>
                            <th>Size</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for cluster in clusters:
            percentage = (cluster['size'] / total_items * 100) if total_items > 0 else 0
            html_content += f"""
                        <tr>
                            <td>Cluster {cluster['label']}</td>
                            <td>{cluster['size']}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Save HTML report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{level}_cluster_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath


# Global instance
visualization_service = VisualizationService()
