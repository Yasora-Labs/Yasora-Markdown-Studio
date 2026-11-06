package org.yasoralabs.markitdown;
import org.junit.Test;
import static org.junit.Assert.*;
public final class DocumentConverterTest {
    @Test public void csvMakesMarkdownTable(){
        String md=DocumentConverter.csvToMarkdown("Name,Score\n\"A,B\",5\n");
        assertTrue(md.contains("| Name | Score |"));
        assertTrue(md.contains("| A,B | 5 |"));
    }
    @Test public void htmlConvertsHeading(){
        assertTrue(DocumentConverter.htmlToMarkdown("<h1>Hello</h1><p>World</p>").contains("# Hello"));
    }
    @Test public void pdfIsClearlyUnsupported() throws Exception {
        try {DocumentConverter.convert("file.pdf",new byte[0]);fail("expected exception");}
        catch(UnsupportedOperationException e){assertTrue(e.getMessage().contains("Windows"));}
    }
}
