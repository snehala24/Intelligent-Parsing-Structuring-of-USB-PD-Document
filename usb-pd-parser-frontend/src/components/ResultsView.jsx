import React from "react";
import { Table, Button } from "antd";

function ResultsView({ results }) {
  const columns = [
    { title: "Section ID", dataIndex: "section_id", key: "section_id" },
    { title: "Title", dataIndex: "title", key: "title" },
    { title: "Page", dataIndex: "page", key: "page" },
    { title: "Level", dataIndex: "level", key: "level" },
  ];

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Parsed Table of Contents</h3>

      <Table
        dataSource={results}
        columns={columns}
        rowKey="section_id"
        pagination={{ pageSize: 10 }}
      />

      {/* ✅ Fixed download buttons to point to backend API */}
      <Button
        type="primary"
        href="http://localhost:8000/download/usb_pd_toc.jsonl"
        target="_blank"
        rel="noopener noreferrer"
        style={{ marginRight: "10px" }}
      >
        Download TOC JSONL
      </Button>

      <Button
        type="primary"
        href="http://localhost:8000/download/usb_pd_spec.jsonl"
        target="_blank"
        rel="noopener noreferrer"
        style={{ marginRight: "10px" }}
      >
        Download Sections JSONL
      </Button>

      <Button
        type="primary"
        href="http://localhost:8000/download/usb_pd_validation_report.xlsx"
        target="_blank"
        rel="noopener noreferrer"
      >
        Download Excel Report
      </Button>
    </div>
  );
}

export default ResultsView;
