import React from "react";
import { useDropzone } from "react-dropzone";
import { uploadPDF } from "../api";
import { UploadOutlined } from "@ant-design/icons";
import { message } from "antd";

function FileUploader({ onUploadComplete }) {
  const { getRootProps, getInputProps } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    onDrop: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file) return;
      message.loading("Uploading and processing, please wait...");
      try {
        const res = await uploadPDF(file);
        message.success("File processed successfully!");
        onUploadComplete(res.data);
      } catch (err) {
        console.error(err);
        message.error("Upload failed");
      }
    },
  });

  return (
    <div
      {...getRootProps()}
      style={{
        border: "2px dashed #1890ff",
        borderRadius: "8px",
        padding: "20px",
        textAlign: "center",
        cursor: "pointer",
      }}
    >
      <input {...getInputProps()} />
      <UploadOutlined style={{ fontSize: "24px", color: "#1890ff" }} />
      <p>Drag & drop your PDF here, or click to select</p>
    </div>
  );
}

export default FileUploader;
