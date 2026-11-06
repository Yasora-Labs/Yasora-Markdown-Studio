package org.yasoralabs.markitdown;

import java.io.ByteArrayOutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import java.nio.charset.StandardCharsets;

/** No Android SDK required: plain Java converter smoke tests. */
public final class StandaloneSmoke {
    private static void require(boolean ok, String why) {if (!ok) throw new AssertionError(why);}
    private static byte[] zip(String fileName, String content) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try(ZipOutputStream z = new ZipOutputStream(out)) {
            z.putNextEntry(new ZipEntry(fileName));
            z.write(content.getBytes(StandardCharsets.UTF_8));
            z.closeEntry();
        }
        return out.toByteArray();
    }
    public static void main(String[] args) throws Exception {
        require(DocumentConverter.csvToMarkdown("Name,Score\n\"A,B\",5\n").contains("| A,B | 5 |"), "CSV");
        require(DocumentConverter.htmlToMarkdown("<h1>Demo</h1><p>Hello</p>").contains("# Demo"), "HTML");
        String docx = "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:body><w:p><w:r><w:t>Hello DOCX</w:t></w:r></w:p></w:body></w:document>";
        require(DocumentConverter.convert("demo.docx", zip("word/document.xml", docx)).contains("Hello DOCX"), "DOCX");
        String pptx = "<p:sld xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\" xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\"><a:p><a:r><a:t>Hello PPTX</a:t></a:r></a:p></p:sld>";
        require(DocumentConverter.convert("demo.pptx", zip("ppt/slides/slide1.xml", pptx)).contains("Hello PPTX"), "PPTX");
        String xlsx = "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\"><v>7</v></c></row></sheetData></worksheet>";
        require(DocumentConverter.convert("demo.xlsx", zip("xl/worksheets/sheet1.xml", xlsx)).contains("| 7 |"), "XLSX");
        try { DocumentConverter.convert("demo.pdf", new byte[0]); throw new AssertionError("PDF should be unsupported"); }
        catch (UnsupportedOperationException expected) { /* alpha limitation */ }
        System.out.println("6 Android converter smoke tests passed");
    }
}
