import pandas as pd
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from config import OUTPUT_CSV, OUTPUT_EXCEL

class DataExporter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export data to CSV format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pakistan_restaurant_leads_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data for export
        export_df = self._prepare_export_data(df)
        
        # Export to CSV
        export_df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Data exported to CSV: {filepath}")
        
        return filepath
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export data to Excel format with multiple sheets"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pakistan_restaurant_leads_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data for export
        export_df = self._prepare_export_data(df)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main data sheet
            export_df.to_excel(writer, sheet_name='All Restaurants', index=False)
            
            # Summary statistics sheet
            self._create_summary_sheet(writer, export_df)
            
            # City-wise breakdown sheet
            self._create_city_breakdown_sheet(writer, export_df)
            
            # Cuisine-wise breakdown sheet
            self._create_cuisine_breakdown_sheet(writer, export_df)
            
            # High-potential leads sheet
            self._create_high_potential_sheet(writer, export_df)
            
            # Data quality analysis sheet
            self._create_quality_analysis_sheet(writer, export_df)
        
        print(f"Data exported to Excel: {filepath}")
        return filepath
    
    def export_to_json(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export data to JSON format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pakistan_restaurant_leads_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert DataFrame to JSON
        data = df.to_dict('records')
        
        # Add metadata
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_restaurants': len(data),
                'cities_covered': df['city'].nunique() if 'city' in df.columns else 0,
                'cuisine_types': df['cuisine_type'].nunique() if 'cuisine_type' in df.columns else 0,
                'data_sources': df['source'].nunique() if 'source' in df.columns else 0
            },
            'restaurants': data
        }
        
        # Export to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Data exported to JSON: {filepath}")
        return filepath
    
    def _prepare_export_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for export by cleaning and organizing columns"""
        export_df = df.copy()
        
        # Reorder columns for better readability
        column_order = [
            'name', 'city', 'cuisine_type', 'phone', 'address', 'website',
            'rating', 'reviews_count', 'lead_score', 'lead_potential',
            'quality_score', 'source', 'description'
        ]
        
        # Add any missing columns with default values
        for col in column_order:
            if col not in export_df.columns:
                export_df[col] = ''
        
        # Reorder columns and add any additional columns
        existing_columns = [col for col in column_order if col in export_df.columns]
        additional_columns = [col for col in export_df.columns if col not in column_order]
        
        final_column_order = existing_columns + additional_columns
        export_df = export_df[final_column_order]
        
        # Clean up data for export
        export_df = export_df.fillna('')
        
        # Format phone numbers
        if 'phone' in export_df.columns:
            export_df['phone'] = export_df['phone'].astype(str).str.replace('nan', '')
        
        # Format ratings
        if 'rating' in export_df.columns:
            export_df['rating'] = export_df['rating'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) and x > 0 else ''
            )
        
        # Format scores
        if 'lead_score' in export_df.columns:
            export_df['lead_score'] = export_df['lead_score'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else ''
            )
        
        if 'quality_score' in export_df.columns:
            export_df['quality_score'] = export_df['quality_score'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else ''
            )
        
        return export_df
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Create summary statistics sheet"""
        summary_data = []
        
        # Basic counts
        summary_data.append(['Total Restaurants', len(df)])
        summary_data.append(['Cities Covered', df['city'].nunique() if 'city' in df.columns else 0])
        summary_data.append(['Cuisine Types', df['cuisine_type'].nunique() if 'cuisine_type' in df.columns else 0])
        summary_data.append(['Data Sources', df['source'].nunique() if 'source' in df.columns else 0])
        
        # Contact information completeness
        if 'phone' in df.columns:
            phone_completeness = (df['phone'] != '').sum() / len(df) * 100
            summary_data.append(['Phone Numbers Available', f"{phone_completeness:.1f}%"])
        
        if 'website' in df.columns:
            website_completeness = (df['website'] != '').sum() / len(df) * 100
            summary_data.append(['Websites Available', f"{website_completeness:.1f}%"])
        
        if 'address' in df.columns:
            address_completeness = (df['address'] != '').sum() / len(df) * 100
            summary_data.append(['Addresses Available', f"{address_completeness:.1f}%"])
        
        # Ratings summary
        if 'rating' in df.columns:
            ratings = pd.to_numeric(df['rating'], errors='coerce')
            valid_ratings = ratings.dropna()
            if len(valid_ratings) > 0:
                summary_data.append(['Average Rating', f"{valid_ratings.mean():.2f}"])
                summary_data.append(['Highest Rating', f"{valid_ratings.max():.1f}"])
                summary_data.append(['Restaurants with Ratings', len(valid_ratings)])
        
        # Lead scoring summary
        if 'lead_score' in df.columns:
            lead_scores = pd.to_numeric(df['lead_score'], errors='coerce')
            valid_scores = lead_scores.dropna()
            if len(valid_scores) > 0:
                summary_data.append(['Average Lead Score', f"{valid_scores.mean():.1f}"])
                summary_data.append(['High Potential Leads', (valid_scores >= 80).sum()])
                summary_data.append(['Medium Potential Leads', ((valid_scores >= 60) & (valid_scores < 80)).sum()])
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Summary']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_city_breakdown_sheet(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Create city-wise breakdown sheet"""
        if 'city' not in df.columns:
            return
        
        city_stats = df.groupby('city').agg({
            'name': 'count',
            'phone': lambda x: (x != '').sum(),
            'website': lambda x: (x != '').sum(),
            'rating': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'lead_score': lambda x: pd.to_numeric(x, errors='coerce').mean()
        }).round(2)
        
        city_stats.columns = ['Total Restaurants', 'With Phone', 'With Website', 'Avg Rating', 'Avg Lead Score']
        city_stats = city_stats.sort_values('Total Restaurants', ascending=False)
        
        city_stats.to_excel(writer, sheet_name='City Breakdown')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['City Breakdown']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_cuisine_breakdown_sheet(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Create cuisine-wise breakdown sheet"""
        if 'cuisine_type' not in df.columns:
            return
        
        cuisine_stats = df.groupby('cuisine_type').agg({
            'name': 'count',
            'phone': lambda x: (x != '').sum(),
            'website': lambda x: (x != '').sum(),
            'rating': lambda x: pd.to_numeric(x, errors='coerce').mean(),
            'lead_score': lambda x: pd.to_numeric(x, errors='coerce').mean()
        }).round(2)
        
        cuisine_stats.columns = ['Total Restaurants', 'With Phone', 'With Website', 'Avg Rating', 'Avg Lead Score']
        cuisine_stats = cuisine_stats.sort_values('Total Restaurants', ascending=False)
        
        cuisine_stats.to_excel(writer, sheet_name='Cuisine Breakdown')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Cuisine Breakdown']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_high_potential_sheet(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Create high-potential leads sheet"""
        if 'lead_score' not in df.columns:
            return
        
        # Filter high-potential leads (score >= 70)
        lead_scores = pd.to_numeric(df['lead_score'], errors='coerce')
        high_potential = df[lead_scores >= 70].copy()
        
        if len(high_potential) > 0:
            # Sort by lead score
            high_potential = high_potential.sort_values('lead_score', ascending=False)
            
            # Select relevant columns
            columns_to_show = ['name', 'city', 'cuisine_type', 'phone', 'website', 'lead_score', 'lead_potential']
            columns_to_show = [col for col in columns_to_show if col in high_potential.columns]
            
            high_potential[columns_to_show].to_excel(writer, sheet_name='High Potential Leads', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['High Potential Leads']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_quality_analysis_sheet(self, writer: pd.ExcelWriter, df: pd.DataFrame):
        """Create data quality analysis sheet"""
        quality_data = []
        
        # Data completeness analysis
        total_records = len(df)
        
        for column in df.columns:
            if column in ['name', 'city', 'phone', 'website', 'address', 'rating']:
                non_empty = (df[column] != '').sum()
                completeness = (non_empty / total_records) * 100
                quality_data.append([column, f"{completeness:.1f}%", non_empty, total_records])
        
        # Source distribution
        if 'source' in df.columns:
            source_dist = df['source'].value_counts()
            for source, count in source_dist.items():
                percentage = (count / total_records) * 100
                quality_data.append([f"Source: {source}", f"{percentage:.1f}%", count, total_records])
        
        # Create quality DataFrame
        quality_df = pd.DataFrame(quality_data, columns=['Field', 'Completeness', 'Count', 'Total'])
        quality_df.to_excel(writer, sheet_name='Data Quality', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Data Quality']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def export_all_formats(self, df: pd.DataFrame, base_filename: str = None) -> Dict[str, str]:
        """Export data to all available formats"""
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"pakistan_restaurant_leads_{timestamp}"
        
        export_files = {}
        
        # Export to CSV
        csv_file = self.export_to_csv(df, f"{base_filename}.csv")
        export_files['csv'] = csv_file
        
        # Export to Excel
        excel_file = self.export_to_excel(df, f"{base_filename}.xlsx")
        export_files['excel'] = excel_file
        
        # Export to JSON
        json_file = self.export_to_json(df, f"{base_filename}.json")
        export_files['json'] = json_file
        
        print(f"\nExport completed! Files saved to {self.output_dir}/")
        print(f"CSV: {os.path.basename(csv_file)}")
        print(f"Excel: {os.path.basename(excel_file)}")
        print(f"JSON: {os.path.basename(json_file)}")
        
        return export_files 