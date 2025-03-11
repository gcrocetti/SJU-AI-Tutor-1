import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { ProgressData } from '../../types';

/**
 * Props for the LineChart component
 */
interface LineChartProps {
  /** Array of data points to render in the chart */
  data: ProgressData[];
  /** Optional width override (in pixels) */
  width?: number;
  /** Optional height override (in pixels) */
  height?: number;
}

/**
 * LineChart Component
 * 
 * A D3.js-powered line chart that visualizes student progress metrics over time.
 * This component creates multiple series lines on the same chart with different colors,
 * along with proper axes, legends, and interactive elements.
 * 
 * The chart automatically adjusts to the container width.
 * 
 * @component
 * @example
 * const data = [
 *   { date: "2024-01", series1: 10, series2: 30, series3: 20 },
 *   { date: "2024-02", series1: 40, series2: 20, series3: 50 }
 * ];
 * return (
 *   <LineChart data={data} height={300} />
 * )
 */
const LineChart: React.FC<LineChartProps> = ({ data, width: propWidth, height: propHeight }) => {
  // Reference to the SVG element
  const chartRef = useRef<SVGSVGElement | null>(null);
  
  /**
   * Effect to create and update the chart when data or dimensions change
   * 
   * This effect handles:
   * - Initial chart creation
   * - Chart updates when data changes
   * - Chart resizing when dimensions change
   * - Cleanup when the component unmounts
   * 
   * TODO: Add more interactive features
   * - Tooltips on hover
   * - Click-to-highlight a specific data point
   * - Animation for transitions between data sets
   * - Zoom functionality for exploring detailed time periods
   */
  useEffect(() => {
    // Don't render if we have no data or DOM element
    if (!data || !chartRef.current) return;
    
    // Clear any existing chart
    const svg = d3.select(chartRef.current);
    svg.selectAll("*").remove();
    
    // Get dimensions from props or calculate from container
    const width = propWidth || chartRef.current.parentElement?.clientWidth || 300;
    const height = propHeight || 250;
    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    
    // Set up scales
    const x = d3.scalePoint<string>()
      .domain(data.map(d => d.date))
      .range([margin.left, width - margin.right]);
    
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.series1, d.series2, d.series3)) || 100])
      .nice()
      .range([height - margin.bottom, margin.top]);
    
    // Set up line generator
    const line = d3.line<{date: string, value: number}>()
      .x(d => x(d.date) || 0)
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX);
    
    // Define colors for each series
    const colors: Record<string, string> = { 
      series1: "#cf102d", // St. John's Red 
      series2: "#e3ba12", // Gold accent
      series3: "#2a5d86"  // Blue accent
    };
    
    // Draw lines for each series
    const seriesNames = Object.keys(colors);
    
    seriesNames.forEach(series => {
      // Map raw data to format needed for line generator
      const seriesData = data.map(d => ({ 
        date: d.date, 
        value: d[series as keyof ProgressData] as number 
      }));
      
      // Draw the line itself
      svg.append("path")
        .datum(seriesData)
        .attr("fill", "none")
        .attr("stroke", colors[series])
        .attr("stroke-width", 2)
        .attr("d", line)
        .attr("opacity", 0)  // Start invisible
        .transition()
        .duration(1000)
        .attr("opacity", 1); // Fade in
        
      // Add dots for each data point
      svg.selectAll(`.dot-${series}`)
        .data(seriesData)
        .enter()
        .append("circle")
        .attr("class", `dot-${series}`)
        .attr("cx", d => x(d.date) || 0)
        .attr("cy", d => y(d.value))
        .attr("r", 4)
        .attr("fill", colors[series])
        .attr("opacity", 0)
        .transition()
        .delay(1000)
        .duration(500)
        .attr("opacity", 1);
    });
    
    // Add X axis
    svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("font-size", "12px");
    
    // Add Y axis
    svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y))
      .selectAll("text")
      .style("font-size", "12px");
      
    // Add legend
    const legend = svg.append("g")
      .attr("transform", `translate(${width - margin.right - 100}, ${margin.top})`);
      
    seriesNames.forEach((series, i) => {
      const legendItem = legend.append("g")
        .attr("transform", `translate(0, ${i * 20})`);
        
      legendItem.append("rect")
        .attr("width", 12)
        .attr("height", 12)
        .attr("fill", colors[series]);
        
      legendItem.append("text")
        .attr("x", 20)
        .attr("y", 10)
        .attr("text-anchor", "start")
        .style("font-size", "12px")
        .text(`Series ${i+1}`);
    });
    
    /**
     * FUTURE ENHANCEMENTS:
     * 
     * 1. Add tooltips on hover using d3.tip
     * 2. Add click interaction to highlight specific data points
     * 3. Add axis labels and chart title
     * 4. Support dark mode with theme-aware colors
     * 5. Add chart export functionality (PNG/SVG)
     * 6. Implement responsive resizing with window resize events
     * 7. Add zoom and pan capabilities for exploring detailed views
     */
    
    // Cleanup function
    return () => {
      svg.selectAll("*").remove();
    };
  }, [data, propWidth, propHeight]);
  
  return <svg ref={chartRef}></svg>;
};

export default LineChart;