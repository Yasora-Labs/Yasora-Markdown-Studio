package org.yasoralabs.markitdown;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/** Offline lightweight Markdown extraction (NOT Microsoft's MarkItDown engine). */
public final class DocumentConverter {
    private DocumentConverter() {}
    public static final int MAX_SOURCE_BYTES = 20 * 1024 * 1024;
    private static final int MAX_UNCOMPRESSED_ENTRY = 8 * 1024 * 1024;
    private static final Pattern SLIDE = Pattern.compile("ppt/slides/slide(\\d+)\\.xml");

    public static String convert(String name, byte[] data) throws Exception {
        if (data.length > MAX_SOURCE_BYTES) throw new IllegalArgumentException("Document exceeds 20 MB size limit.");
        String ext = name.toLowerCase(Locale.ROOT).replaceAll("^.*(\\.[^.]+)$", "$1");
        String text = new String(data, StandardCharsets.UTF_8).replace("\uFEFF", "");
        String title = "# " + name.replace("\n", " ").replace("\r", " ") + "\n\n";
        switch (ext) {
            case ".txt": case ".md": return title + text.trim() + "\n";
            case ".json": return title + "```json\n" + text.trim() + "\n```\n";
            case ".xml": return title + "```xml\n" + text.trim() + "\n```\n";
            case ".csv": return title + csvToMarkdown(text);
            case ".htm": case ".html": return title + htmlToMarkdown(text);
            case ".docx": return title + docxToMarkdown(data);
            case ".pptx": return title + pptxToMarkdown(data);
            case ".xlsx": return title + xlsxToMarkdown(data);
            case ".pdf": throw new UnsupportedOperationException("PDF conversion is available in the Windows MarkItDown app, not this offline Android MVP.");
            default: throw new UnsupportedOperationException("Unsupported format: " + ext + ". Supported: TXT, MD, HTML, CSV, JSON, XML, DOCX, PPTX, XLSX.");
        }
    }

    public static String csvToMarkdown(String text) {
        List<List<String>> rows = new ArrayList<>();
        List<String> row = new ArrayList<>();
        StringBuilder field = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c == '"') {
                if (quoted && i + 1 < text.length() && text.charAt(i+1) == '"') { field.append('"'); i++; }
                else quoted = !quoted;
            } else if (c == ',' && !quoted) {
                row.add(field.toString()); field.setLength(0);
            } else if ((c == '\r' || c == '\n') && !quoted) {
                if (c == '\r' && i+1 < text.length() && text.charAt(i+1) == '\n') i++;
                row.add(field.toString()); field.setLength(0);
                rows.add(row); row = new ArrayList<>();
                if (rows.size() >= 10000) break;
            } else { field.append(c); }
        }
        if (field.length() > 0 || !row.isEmpty()) { row.add(field.toString()); rows.add(row); }
        return markdownTable(rows);
    }

    private static String markdownTable(List<List<String>> rows) {
        if (rows.isEmpty()) return "_(No rows)_\n";
        int cols = Math.min(32, rows.get(0).size());
        StringBuilder out = new StringBuilder();
        appendRow(out, rows.get(0), cols);
        out.append('|'); for (int i=0; i<cols; i++) out.append(" --- |"); out.append('\n');
        for (int i=1; i<rows.size() && i<=5000; i++) appendRow(out, rows.get(i), cols);
        if (rows.size() > 5001) out.append("\n_(Truncated to 5,000 data rows)_\n");
        return out.toString();
    }
    private static void appendRow(StringBuilder out, List<String> values, int cols) {
        out.append('|');
        for (int j=0; j<cols; j++) {
            String v = j < values.size() ? values.get(j) : "";
            out.append(' ').append(v.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")).append(" |");
        }
        out.append('\n');
    }

    public static String htmlToMarkdown(String html) {
        html = html.replaceAll("(?is)<(script|style)\\b[^>]*>.*?</\\1\\s*>", "");
        for (int i=6; i>=1; i--) html = html.replaceAll("(?is)<h" + i + "\\b[^>]*>", "\n\n" + hashes(i) + " ");
        html = html.replaceAll("(?is)</h[1-6]\\s*>", "\n\n")
                   .replaceAll("(?is)<li\\b[^>]*>", "\n- ")
                   .replaceAll("(?is)<br\\b[^>]*>", "\n")
                   .replaceAll("(?is)</(p|div|ul|ol|section|article)\\s*>", "\n\n")
                   .replaceAll("(?is)<[^>]+>", "");
        html = html.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"")
                   .replace("&#39;", "'").replace("&nbsp;", " ").replace("&amp;", "&");
        return html.replaceAll("(?m)[ \\t]+$", "").replaceAll("\n{3,}", "\n\n").trim() + "\n";
    }
    private static String hashes(int count) { StringBuilder s=new StringBuilder(); for(int i=0;i<count;i++) s.append('#'); return s.toString(); }

    private static Document parseXml(byte[] bytes) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
        f.setNamespaceAware(true);
        f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        f.setFeature("http://xml.org/sax/features/external-general-entities", false);
        f.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        f.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        f.setXIncludeAware(false);
        f.setExpandEntityReferences(false);
        f.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        f.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
        return f.newDocumentBuilder().parse(new ByteArrayInputStream(bytes));
    }
    private static List<Element> elements(Document doc, String local) {
        NodeList list = doc.getElementsByTagNameNS("*", local);
        List<Element> out = new ArrayList<>();
        for (int i=0; i<list.getLength(); i++) if(list.item(i) instanceof Element) out.add((Element) list.item(i));
        return out;
    }
    private static String joinedText(Element parent, String tag) {
        NodeList list = parent.getElementsByTagNameNS("*", tag);
        StringBuilder sb=new StringBuilder();
        for(int i=0;i<list.getLength();i++) sb.append(list.item(i).getTextContent());
        return sb.toString();
    }
    private static byte[] getZipEntry(byte[] data, String entryName) throws Exception {
        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(data))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                if (entryName.equals(entry.getName())) return readEntry(zis);
            }
        }
        return null;
    }
    private static byte[] readEntry(ZipInputStream zis) throws Exception {
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        byte[] buf=new byte[8192]; int n;
        while ((n=zis.read(buf))!=-1) {
            if (out.size()+n>MAX_UNCOMPRESSED_ENTRY) throw new IllegalArgumentException("Archive entry too large.");
            out.write(buf,0,n);
        }
        return out.toByteArray();
    }

    private static String docxToMarkdown(byte[] data) throws Exception {
        byte[] xml = getZipEntry(data, "word/document.xml");
        if (xml==null) throw new IllegalArgumentException("Not a valid DOCX file: word/document.xml missing.");
        Document doc=parseXml(xml); StringBuilder out=new StringBuilder();
        for (Element p: elements(doc,"p")) {
            String content=joinedText(p,"t").trim();
            if (content.isEmpty()) continue;
            String style="";
            NodeList styles=p.getElementsByTagNameNS("*","pStyle");
            if(styles.getLength()>0) {
                Element el=(Element)styles.item(0);
                style=el.getAttributeNS("http://schemas.openxmlformats.org/wordprocessingml/2006/main","val");
            }
            if(style.matches("(?i)heading[1-6]")) {
                int level=Integer.parseInt(style.substring(style.length()-1));
                out.append(hashes(level)).append(' ');
            }
            out.append(content).append("\n\n");
        }
        return out.length()==0?"_(No extractable text)_\n":out.toString();
    }
    private static String pptxToMarkdown(byte[] data) throws Exception {
        List<String> names=new ArrayList<>();
        try(ZipInputStream zis=new ZipInputStream(new ByteArrayInputStream(data))){ ZipEntry e;
            while((e=zis.getNextEntry())!=null){ if(SLIDE.matcher(e.getName()).matches()) names.add(e.getName()); }
        }
        Collections.sort(names, Comparator.comparingInt(n->{ Matcher m=SLIDE.matcher(n); return m.matches()?Integer.parseInt(m.group(1)):0; }));
        StringBuilder out=new StringBuilder();
        for(String name:names) {
            Matcher m=SLIDE.matcher(name); m.matches(); String num=m.group(1);
            out.append("## Slide ").append(num).append("\n\n");
            byte[] xml=getZipEntry(data,name);
            if(xml==null)continue;
            for(Element p:elements(parseXml(xml),"p")){
                String line=joinedText(p,"t").trim(); if(!line.isEmpty())out.append(line).append("\n\n");
            }
        }
        return out.length()==0?"_(No extractable slide text)_\n":out.toString();
    }
    private static String xlsxToMarkdown(byte[] data) throws Exception {
        List<String> shared=new ArrayList<>();
        byte[] sst=getZipEntry(data,"xl/sharedStrings.xml");
        if(sst!=null) for(Element si:elements(parseXml(sst),"si")) shared.add(joinedText(si,"t"));
        List<String> sheets=new ArrayList<>();
        try(ZipInputStream zis=new ZipInputStream(new ByteArrayInputStream(data))){ ZipEntry e;
            while((e=zis.getNextEntry())!=null) if(e.getName().matches("xl/worksheets/sheet\\d+\\.xml")) sheets.add(e.getName());
        }
        Collections.sort(sheets);
        StringBuilder out=new StringBuilder();
        for(String path:sheets){
            out.append("## ").append(path.substring(path.lastIndexOf('/')+1).replace(".xml", "")).append("\n\n");
            byte[] xml=getZipEntry(data,path); if(xml==null)continue;
            List<List<String>> rows=new ArrayList<>();
            for(Element row:elements(parseXml(xml),"row")) {
                List<String> values=new ArrayList<>();
                NodeList cells=row.getElementsByTagNameNS("*","c");
                for(int i=0;i<cells.getLength() && i<32;i++) {
                    Element cell=(Element)cells.item(i); String raw=joinedText(cell,"v");
                    if("s".equals(cell.getAttribute("t"))){
                        try{ int index=Integer.parseInt(raw); raw=index>=0 && index<shared.size()?shared.get(index):""; } catch(NumberFormatException ignored){raw="";}
                    } else if("inlineStr".equals(cell.getAttribute("t")))raw=joinedText(cell,"t");
                    values.add(raw);
                }
                if(!values.isEmpty())rows.add(values);
                if(rows.size()>5001) break;
            }
            out.append(markdownTable(rows)).append('\n');
        }
        return out.length()==0?"_(No extractable spreadsheet text)_\n":out.toString();
    }
}
