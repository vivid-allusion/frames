"""Report generation for costs and status."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from ..output.writer import OutputWriter


class Reporter:
    """Generate markdown reports for runs."""
    
    def __init__(self, output_writer: OutputWriter):
        """
        Initialize reporter.
        
        Args:
            output_writer: OutputWriter instance
        """
        self.output_writer = output_writer
        self.start_time = datetime.now()
    
    def save_reports(
        self,
        success: bool,
        summary: Dict[str, Any],
        error_message: Optional[str] = None,
        profiles_with_fixes: Optional[List[Dict[str, str]]] = None
    ) -> None:
        """
        Save all reports based on run outcome.
        
        Args:
            success: Whether run was successful
            summary: Processing summary with metrics
            error_message: Error message if failed
            profiles_with_fixes: List of profiles with prompt fixes
        """
        if success:
            self._save_success_reports(summary, profiles_with_fixes)
        else:
            self._save_failure_report(summary, error_message, profiles_with_fixes)
    
    def _save_success_reports(
        self,
        summary: Dict[str, Any],
        profiles_with_fixes: Optional[List[Dict[str, str]]] = None
    ) -> None:
        """Save success and cost reports."""
        # Generate success report
        success_report = self._generate_success_report(summary)
        self.output_writer.write_report(success_report, "SUCCESS.md")
        
        # Generate cost report if applicable
        if summary.get('total_cost', 0) > 0:
            cost_report = self._generate_cost_report(summary)
            self.output_writer.write_report(cost_report, "COST-REPORT.md")
        
        # Generate profiles report if fixes exist
        if profiles_with_fixes:
            profiles_report = self._generate_profiles_report(profiles_with_fixes)
            self.output_writer.write_report(profiles_report, "PROFILES-WITH-FIXES.md")
        
        logger.info("Reports saved successfully")
    
    def _save_failure_report(
        self,
        summary: Dict[str, Any],
        error_message: Optional[str],
        profiles_with_fixes: Optional[List[Dict[str, str]]] = None
    ) -> None:
        """Save failure report."""
        failure_report = self._generate_failure_report(summary, error_message)
        self.output_writer.write_report(failure_report, "FAILURE.md")
        
        # Still save cost report if any processing happened
        if summary.get('processed', 0) > 0 and summary.get('total_cost', 0) > 0:
            cost_report = self._generate_cost_report(summary)
            self.output_writer.write_report(cost_report, "PARTIAL-COST-REPORT.md")
        
        logger.error("Failure report saved")
    
    def _generate_success_report(self, summary: Dict[str, Any]) -> str:
        """Generate success report content."""
        processing_time = (datetime.now() - self.start_time).total_seconds()
        
        report_lines = [
            "# SUCCESS",
            "",
            "## Run Summary",
            f"- **Status**: ✅ Completed Successfully",
            f"- **Total Images Generated**: {summary.get('processed', 0)}",
            f"- **Total Prompts**: {summary.get('total_prompts', 0)}",
            f"- **Total Models**: {summary.get('total_models', 0)}",
            f"- **Processing Time**: {processing_time:.2f} seconds",
            ""
        ]
        
        # Add metrics if available
        if summary.get('processed', 0) > 0:
            avg_time = processing_time / summary['processed']
            report_lines.extend([
                "## Performance Metrics",
                f"- **Average Time per Image**: {avg_time:.2f} seconds",
                f"- **Success Rate**: 100.0%",
                ""
            ])
        
        # Add timestamp
        report_lines.extend([
            f"*Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _generate_cost_report(self, summary: Dict[str, Any]) -> str:
        """Generate cost report content."""
        total_cost = summary.get('total_cost', 0)
        processed = summary.get('processed', 0)
        
        report_lines = [
            "# Cost Report",
            "",
            "## Summary",
            f"- **Total Images Generated**: {processed}",
            f"- **Total Cost**: ${total_cost:.4f}",
        ]
        
        if processed > 0:
            avg_cost = total_cost / processed
            report_lines.append(f"- **Average Cost per Image**: ${avg_cost:.4f}")
        
        report_lines.extend([
            "",
            f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _generate_failure_report(
        self,
        summary: Dict[str, Any],
        error_message: Optional[str]
    ) -> str:
        """Generate failure report content."""
        processing_time = (datetime.now() - self.start_time).total_seconds()
        
        report_lines = [
            "# FAILURE",
            "",
            "## Run Summary",
            f"- **Status**: ❌ Failed",
            f"- **Images Generated Before Failure**: {summary.get('processed', 0)}",
            f"- **Failed Operations**: {summary.get('failed', 0)}",
            f"- **Processing Time**: {processing_time:.2f} seconds",
            ""
        ]
        
        if error_message:
            report_lines.extend([
                "## Error Details",
                f"```",
                f"{error_message}",
                f"```",
                ""
            ])
        
        # Add partial results if any
        if summary.get('processed', 0) > 0:
            report_lines.extend([
                "## Partial Results",
                f"- **Successfully Generated**: {summary['processed']} images",
                f"- **Partial Cost**: ${summary.get('total_cost', 0):.4f}",
                ""
            ])
        
        report_lines.extend([
            f"*Failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _generate_profiles_report(
        self,
        profiles_with_fixes: List[Dict[str, str]]
    ) -> str:
        """Generate report of profiles that have prompt fixes."""
        report_lines = [
            "# Profiles with Prompt Modifications",
            "",
            "The following profiles modified prompts with prefixes or suffixes:",
            ""
        ]
        
        for profile in profiles_with_fixes:
            report_lines.append(f"## {profile['profile_name']}")
            
            if profile.get('prompt_prefix'):
                report_lines.append(f"- **Prefix**: `{profile['prompt_prefix']}`")
            
            if profile.get('prompt_suffix'):
                report_lines.append(f"- **Suffix**: `{profile['prompt_suffix']}`")
            
            report_lines.append("")
        
        report_lines.extend([
            f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])
        
        return "\n".join(report_lines)