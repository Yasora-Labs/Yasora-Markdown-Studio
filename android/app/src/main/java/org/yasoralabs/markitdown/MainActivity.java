package org.yasoralabs.markitdown;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** No INTERNET permission; user-selected SAF file in, SAF .md out. */
public final class MainActivity extends Activity {
    private static final int PICK_DOCUMENT = 101;
    private static final int SAVE_MARKDOWN = 102;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private TextView status;
    private TextView preview;
    private Button saveButton;
    private Button shareButton;
    private ProgressBar progress;
    private String markdown = "";
    private String filename = "document";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(22, 31, 84));
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dp(20), dp(16), dp(20), dp(16));
        layout.setBackgroundColor(Color.rgb(248, 250, 255));

        ImageView icon = new ImageView(this);
        icon.setImageResource(R.drawable.studio_icon);
        LinearLayout.LayoutParams iconSize = new LinearLayout.LayoutParams(dp(74), dp(74));
        iconSize.gravity=Gravity.CENTER_HORIZONTAL;
        layout.addView(icon,iconSize);

        TextView header=new TextView(this);
        header.setText("Yasora Markdown Studio"); header.setTextSize(22); header.setTextColor(Color.rgb(25,45,91)); header.setGravity(Gravity.CENTER);
        layout.addView(header);
        TextView description=new TextView(this);
        description.setText("Offline Android companion · limited local conversion");
        description.setTextSize(13); description.setTextColor(Color.DKGRAY); description.setGravity(Gravity.CENTER);
        layout.addView(description);

        Button choose = new Button(this); choose.setText("Choose a document");
        choose.setOnClickListener(v -> chooseDocument()); layout.addView(choose);

        saveButton = new Button(this); saveButton.setText("Save Markdown (.md)"); saveButton.setEnabled(false);
        saveButton.setOnClickListener(v -> saveMarkdown()); layout.addView(saveButton);

        shareButton = new Button(this); shareButton.setText("Share Markdown text"); shareButton.setEnabled(false);
        shareButton.setOnClickListener(v -> shareMarkdown()); layout.addView(shareButton);

        Button updates = new Button(this); updates.setText("Check updates on GitHub");
        updates.setOnClickListener(v -> {
            Intent browser = new Intent(Intent.ACTION_VIEW,
                Uri.parse("https://github.com/Yasora-Labs/Yasora-Markdown-Studio/releases/latest"));
            try { startActivity(browser); }
            catch (ActivityNotFoundException ex) { Toast.makeText(this, "No browser available", Toast.LENGTH_LONG).show(); }
        });
        layout.addView(updates);

        progress=new ProgressBar(this); progress.setVisibility(View.GONE); layout.addView(progress);
        status=new TextView(this); status.setText("Ready. TXT, MD, HTML, CSV, JSON, XML, DOCX, PPTX, XLSX only.");
        status.setTextColor(Color.rgb(52,75,104)); status.setPadding(0,dp(8),0,dp(8)); layout.addView(status);

        ScrollView scroll=new ScrollView(this);
        preview=new TextView(this); preview.setTextSize(13); preview.setTextColor(Color.BLACK); preview.setTextIsSelectable(true);
        preview.setText("Choose a file to preview its Markdown. The original file stays unchanged.\n\nPDF and image OCR require a future conversion engine; they are not supported in this offline MVP.");
        preview.setPadding(dp(8), dp(12), dp(8), dp(12)); scroll.addView(preview);
        layout.addView(scroll, new LinearLayout.LayoutParams(-1,0,1));
        setContentView(layout);
        acceptShareIntent(getIntent());
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        acceptShareIntent(intent);
    }
    private void acceptShareIntent(Intent intent) {
        if (intent == null || !Intent.ACTION_SEND.equals(intent.getAction())) return;
        Uri shared = intent.getParcelableExtra(Intent.EXTRA_STREAM);
        if (shared != null) {
            convertUri(shared);
        } else {
            CharSequence text = intent.getCharSequenceExtra(Intent.EXTRA_TEXT);
            if (text != null) {
                markdown = "# Shared text\n\n" + text.toString();
                filename = "shared-text";
                preview.setText(markdown);
                status.setText("Text received; ready to save as Markdown.");
                saveButton.setEnabled(true);
                shareButton.setEnabled(true);
            }
        }
    }
    private int dp(int x){ return Math.round(x*getResources().getDisplayMetrics().density); }
    private void chooseDocument(){
        Intent picker=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        picker.setType("*/*"); picker.addCategory(Intent.CATEGORY_OPENABLE);
        startActivityForResult(picker,PICK_DOCUMENT);
    }
    private void saveMarkdown(){
        if(markdown.isEmpty()) return;
        Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT);
        save.addCategory(Intent.CATEGORY_OPENABLE); save.setType("text/markdown");
        save.putExtra(Intent.EXTRA_TITLE,filename+".md");
        startActivityForResult(save,SAVE_MARKDOWN);
    }
    private void shareMarkdown(){
        if(markdown.isEmpty())return;
        if(markdown.length()>100000){
            Toast.makeText(this,"Too large for text sharing: use Save Markdown first.",Toast.LENGTH_LONG).show();
            return;
        }
        Intent intent=new Intent(Intent.ACTION_SEND);
        intent.setType("text/plain"); intent.putExtra(Intent.EXTRA_TEXT,markdown);
        startActivity(Intent.createChooser(intent,"Share Markdown"));
    }
    @Override protected void onActivityResult(int requestCode, int resultCode, Intent result){
        super.onActivityResult(requestCode,resultCode,result);
        if(resultCode!=RESULT_OK || result==null || result.getData()==null)return;
        Uri uri=result.getData();
        if(requestCode==PICK_DOCUMENT){
            convertUri(uri);
        } else if(requestCode==SAVE_MARKDOWN){
            final String snapshot=markdown;
            executor.execute(()->{
                try(OutputStream out=getContentResolver().openOutputStream(uri,"w")){
                    if(out==null)throw new IllegalArgumentException("Could not save output.");
                    out.write(snapshot.getBytes(StandardCharsets.UTF_8)); out.flush();
                    runOnUiThread(()->status.setText("Saved Markdown successfully."));
                } catch(Exception ex){runOnUiThread(()->status.setText("Save failed: "+ex.getMessage()));}
            });
        }
    }
    private void convertUri(Uri uri){
        filename=getDisplayName(uri);
        final String currentFile=filename;
        progress.setVisibility(View.VISIBLE); status.setText("Converting " + currentFile + " locally...");
        saveButton.setEnabled(false); shareButton.setEnabled(false); markdown="";
        executor.execute(()->{
            try(InputStream in=getContentResolver().openInputStream(uri)){
                if(in==null)throw new IllegalArgumentException("Could not open selected document.");
                byte[] bytes=readBounded(in);
                String resultMd=DocumentConverter.convert(currentFile,bytes);
                runOnUiThread(()->{
                    markdown=resultMd; status.setText("Converted: " + currentFile);
                    preview.setText(resultMd); progress.setVisibility(View.GONE);
                    saveButton.setEnabled(true); shareButton.setEnabled(true);
                });
            } catch(Exception ex) {
                runOnUiThread(()->{
                    status.setText("Conversion failed: " + ex.getMessage());
                    progress.setVisibility(View.GONE);
                    preview.setText("No output created.\n" + ex.getMessage());
                });
            }
        });
    }
    private String getDisplayName(Uri uri){
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){
            if(c!=null && c.moveToFirst()){ String v=c.getString(0); if(v!=null)return v; }
        }catch(Exception ignored){}
        return "document.txt";
    }
    private byte[] readBounded(InputStream stream)throws Exception{
        ByteArrayOutputStream out=new ByteArrayOutputStream(); byte[] chunk=new byte[8192]; int n;
        while((n=stream.read(chunk))!=-1){
            if(out.size()+n>DocumentConverter.MAX_SOURCE_BYTES)throw new IllegalArgumentException("File larger than 20 MB.");
            out.write(chunk,0,n);
        }
        return out.toByteArray();
    }
    @Override protected void onDestroy(){executor.shutdownNow(); super.onDestroy();}
}
