package uz.shirin.ai;

import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.*;
import android.provider.MediaStore;
import android.speech.tts.*;
import android.webkit.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
  private static final String ORIGIN="https://appassets.androidplatform.net";
  private static final String HOME=ORIGIN+"/assets/index.html";
  private WebView web;
  private ValueCallback<Uri[]> chooser;
  private PermissionRequest pendingPermission;
  private TextToSpeech tts;
  private boolean ttsReady=false;
  private volatile boolean trustedPage=true;
  private volatile String nextImagePicker="gallery";
  private boolean exportActive=false,exportInterrupted=false;
  private SharedPreferences prefs;
  private FileOutputStream downloadStream;
  private File downloadFile,pendingSave;
  private String downloadTicket,downloadName,downloadMime;
  private boolean downloadToGallery=false;
  private long downloadExpected,downloadWritten;
  private final Map<String,File> speechFiles=new ConcurrentHashMap<>();
  private final Map<String,ServerHttp.Call> serverCalls=new ConcurrentHashMap<>();
  private final Map<String,File> serverMedia=new ConcurrentHashMap<>();
  private final Map<String,String> serverMediaTypes=new ConcurrentHashMap<>();
  private final ExecutorService serverWorkers=Executors.newFixedThreadPool(2);

  @Override public void onCreate(Bundle state){
    super.onCreate(state);
    prefs=getSharedPreferences("shirin",MODE_PRIVATE);
    File[] cachedMedia=getCacheDir().listFiles((dir,name)->name.startsWith("server-media-"));
    if(cachedMedia!=null)for(File file:cachedMedia)if(file.isFile())file.delete();
    LinearLayout root=new LinearLayout(this);root.setOrientation(1);root.setBackgroundColor(0xff080d17);
    root.setOnApplyWindowInsetsListener((view,insets)->{view.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets;});
    web=new WebView(this);web.setBackgroundColor(0xff080d17);root.addView(web,new LinearLayout.LayoutParams(-1,-1));setContentView(root);
    WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);settings.setDatabaseEnabled(true);settings.setAllowFileAccess(false);settings.setAllowContentAccess(true);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);settings.setMediaPlaybackRequiresUserGesture(false);settings.setTextZoom(100);
    web.addJavascriptInterface(new Bridge(),"ShirinNative");
    web.setWebViewClient(new WebViewClient(){
      @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap icon){trustedPage=url!=null&&url.startsWith(ORIGIN+"/assets/");}
      @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
        Uri uri=request.getUrl();if(uri.toString().startsWith(ORIGIN+"/assets/"))return false;
        if(request.isForMainFrame()&&"https".equals(uri.getScheme())){try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception ignored){}}
        return true;
      }
      @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){
        Uri uri=request.getUrl();if(!"https".equals(uri.getScheme())||!"appassets.androidplatform.net".equals(uri.getHost()))return null;
        String path=uri.getPath();
        try{
          InputStream input;String mime;
          if(path!=null&&path.matches("/assets/[A-Za-z0-9._-]+")){
            String name=path.substring(8);input=getAssets().open(name);
            mime=name.endsWith(".html")?"text/html":name.endsWith(".js")?"text/javascript":name.endsWith(".css")?"text/css":name.endsWith(".svg")?"image/svg+xml":"application/json";
          }else if(path!=null&&path.matches("/legacy/(img-[a-zA-Z0-9-]+\\.jpg|selected-image\\.jpg)")){
            File f=new File(getFilesDir(),path.substring(8));if(!f.isFile())throw new FileNotFoundException();input=new FileInputStream(f);mime="image/jpeg";
          }else if(path!=null&&path.matches("/generated/tts-[0-9]+\\.wav")){
            File f=new File(getCacheDir(),path.substring(11));if(!f.isFile())throw new FileNotFoundException();input=new FileInputStream(f);mime="audio/wav";
          }else if(path!=null&&path.matches("/server-media/[A-Za-z0-9-]{1,80}")){
            String ticket=path.substring(14);File f=serverMedia.get(ticket);String type=serverMediaTypes.get(ticket);
            if(f==null||type==null||!f.isFile())throw new FileNotFoundException();input=new FileInputStream(f);mime=type;
          }else throw new FileNotFoundException();
          Map<String,String> headers=new HashMap<>();headers.put("Cache-Control","no-store");headers.put("X-Content-Type-Options","nosniff");headers.put("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob: data: https:; connect-src 'self' https:; object-src 'none'; frame-src 'none'; base-uri 'self'");
          return new WebResourceResponse(mime,"UTF-8",200,"OK",headers,input);
        }catch(Exception e){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",null,new ByteArrayInputStream(new byte[0]));}
      }
    });
    web.setWebChromeClient(new WebChromeClient(){
      @Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){
        if(chooser!=null)chooser.onReceiveValue(null);chooser=callback;
        ArrayList<String> types=new ArrayList<>();for(String accept:params.getAcceptTypes())for(String type:accept.split(","))if(type.contains("/"))types.add(type.trim());
        boolean multiple=params.getMode()==FileChooserParams.MODE_OPEN_MULTIPLE;
        boolean onlyImages=!types.isEmpty();for(String type:types)if(!type.startsWith("image/"))onlyImages=false;
        String picker=nextImagePicker;nextImagePicker="gallery";
        if(onlyImages&&"gallery".equals(picker)){
          try{
            Intent gallery;
            if(Build.VERSION.SDK_INT>=33){gallery=new Intent(MediaStore.ACTION_PICK_IMAGES);gallery.setType("image/*");if(multiple)gallery.putExtra(MediaStore.EXTRA_PICK_IMAGES_MAX,Math.min(100,MediaStore.getPickImagesMaxLimit()));}
            else{gallery=new Intent(Intent.ACTION_GET_CONTENT);gallery.addCategory(Intent.CATEGORY_OPENABLE);gallery.setType("image/*");gallery.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,multiple);}
            gallery.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivityForResult(gallery,10);return true;
          }catch(Exception ignored){}
        }
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType(onlyImages?"image/*":"*/*");
        if(!types.isEmpty())intent.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,multiple);
        try{startActivityForResult(intent,10);return true;}catch(Exception e){chooser.onReceiveValue(null);chooser=null;return false;}
      }
      @Override public void onPermissionRequest(PermissionRequest request){
        runOnUiThread(()->{
          if(!ORIGIN.equals(request.getOrigin().toString().replaceAll("/$",""))||!Arrays.asList(request.getResources()).contains(PermissionRequest.RESOURCE_AUDIO_CAPTURE)){request.deny();return;}
          if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)==PackageManager.PERMISSION_GRANTED)request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
          else {pendingPermission=request;requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},30);}
        });
      }
      @Override public void onPermissionRequestCanceled(PermissionRequest request){if(pendingPermission==request)pendingPermission=null;}
    });
    tts=new TextToSpeech(this,status->{ttsReady=status==TextToSpeech.SUCCESS;});
    tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){
      public void onStart(String utteranceId){}
      public void onError(String utteranceId){speechFiles.remove(utteranceId);voiceError("Qurilma ovozni yarata olmadi.");}
      public void onDone(String utteranceId){File file=speechFiles.remove(utteranceId);if(file!=null){try{JSONObject obj=new JSONObject();obj.put("url",ORIGIN+"/generated/"+file.getName());callback("onNativeVoice",obj);}catch(Exception ignored){}}}
    });
    web.loadUrl(HOME);
  }
  private void callback(String method,JSONObject data){runOnUiThread(()->{if(trustedPage)web.evaluateJavascript("window."+method+" && window."+method+"("+data.toString()+");",null);});}
  private void voiceError(String message){try{callback("onNativeVoice",new JSONObject().put("error",message));}catch(Exception ignored){}}
  private void downloadMessage(String message){runOnUiThread(()->web.evaluateJavascript("window.onNativeDownload && window.onNativeDownload("+JSONObject.quote(message)+");",null));}
  private void saveMediaToGallery(final File file,final String name,final String mime){
    new Thread(()->{
      Uri target=null;
      try{
        boolean image=mime.startsWith("image/");ContentValues values=new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME,name);values.put(MediaStore.MediaColumns.MIME_TYPE,mime);
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,(image?Environment.DIRECTORY_PICTURES:Environment.DIRECTORY_MOVIES)+"/Shirin AI");values.put(MediaStore.MediaColumns.IS_PENDING,1);
        target=getContentResolver().insert(image?MediaStore.Images.Media.EXTERNAL_CONTENT_URI:MediaStore.Video.Media.EXTERNAL_CONTENT_URI,values);
        if(target==null)throw new IOException();
        try(InputStream input=new FileInputStream(file);OutputStream output=getContentResolver().openOutputStream(target)){
          if(output==null)throw new IOException();byte[] buffer=new byte[65536];int n;while((n=input.read(buffer))!=-1)output.write(buffer,0,n);
        }
        values.clear();values.put(MediaStore.MediaColumns.IS_PENDING,0);getContentResolver().update(target,values,null,null);downloadMessage("Telefon galereyasiga saqlandi · Shirin AI.");
      }catch(Exception e){if(target!=null)try{getContentResolver().delete(target,null,null);}catch(Exception ignored){}downloadMessage("Telefon galereyasiga saqlanmadi. Yuklash tugmasidan foydalan.");}
      finally{file.delete();}
    }).start();
  }

  public class Bridge {
    @JavascriptInterface public synchronized void requestServer(String raw){
      if(!trustedPage)return;
      String ticket="";
      try{
        if(raw==null||raw.length()>270*1024*1024)throw new IOException("Yuklama juda katta.");
        final JSONObject request=new JSONObject(raw);ticket=request.optString("id");
        if(!ticket.matches("[A-Za-z0-9-]{1,80}")||serverCalls.containsKey(ticket))return;
        if(serverCalls.size()>=8)throw new IOException("Avvalgi server so‘rovi tugashini kut.");
        final String id=ticket;final ServerHttp.Call call=new ServerHttp.Call();serverCalls.put(id,call);
        serverWorkers.execute(()->{
          File file=null;
          try{
            JSONObject reply=new JSONObject().put("id",id);
            if("media".equals(request.optString("type"))){
              file=new File(getCacheDir(),"server-media-"+id);
              String mime=call.media(request.getString("base"),request.getString("url"),file,request.optInt("timeout",180000));
              serverMediaTypes.put(id,mime);serverMedia.put(id,file);
              reply.put("url",ORIGIN+"/server-media/"+id).put("mime",mime);
            }else{
              ServerHttp.Reply result=call.json(request.getString("base"),request.getString("path"),request.optString("token"),request.isNull("body")?null:request.getString("body"),request.optInt("timeout",15000));
              reply.put("status",result.status).put("body",result.body);
            }
            callback("onNativeServerResult",reply);
          }catch(Exception e){if(file!=null)file.delete();serverMedia.remove(id);serverMediaTypes.remove(id);serverFailure(id,e);}
          finally{serverCalls.remove(id);if(!trustedPage){serverMediaTypes.remove(id);File stale=serverMedia.remove(id);if(stale!=null)stale.delete();}}
        });
      }catch(Exception e){if(!ticket.isEmpty()){ServerHttp.Call call=serverCalls.remove(ticket);if(call!=null)call.cancel();serverFailure(ticket,e);}}
    }
    @JavascriptInterface public void cancelServerRequest(String ticket){if(!trustedPage)return;ServerHttp.Call call=serverCalls.get(ticket);if(call!=null)call.cancel();releaseServerMedia(ticket);}
    @JavascriptInterface public void releaseServerMedia(String ticket){if(!trustedPage)return;serverMediaTypes.remove(ticket);File file=serverMedia.remove(ticket);if(file!=null)file.delete();}
    @JavascriptInterface public void setExportActive(boolean active){
      if(!trustedPage)return;
      runOnUiThread(()->{exportActive=active;if(active)getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);else{getWindow().clearFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);exportInterrupted=false;}});
    }
    @JavascriptInterface public void setImagePicker(String mode){if(trustedPage)nextImagePicker="files".equals(mode)?"files":"gallery";}
    @JavascriptInterface public String getSettings(){
      if(!trustedPage)return "{}";
      try{String saved=prefs.getString("studio_settings","");if(!saved.isEmpty())return saved;JSONObject obj=new JSONObject();obj.put("base",prefs.getString("server",""));obj.put("token",prefs.getString("token",""));obj.put("remember",false);return obj.toString();}catch(Exception e){return "{}";}
    }
    @JavascriptInterface public String getLegacyDraft(){
      if(!trustedPage)return "{}";
      try{JSONObject result=new JSONObject();JSONArray files=new JSONArray(),old=new JSONArray(prefs.getString("image_files","[]"));
        for(int i=0;i<old.length();i++){String name=old.optString(i);if(name.matches("img-[a-zA-Z0-9-]+\\.jpg")&&new File(getFilesDir(),name).isFile())files.put(name);}
        if(files.length()==0&&!prefs.contains("image_files")&&new File(getFilesDir(),"selected-image.jpg").isFile())files.put("selected-image.jpg");
        result.put("files",files);result.put("prompt",prefs.getString("draft",""));return result.toString();
      }catch(Exception e){return "{}";}
    }
    @JavascriptInterface public void saveSettings(String value){
      if(!trustedPage)return;try{JSONObject obj=new JSONObject(value);String base=obj.optString("base");if(!base.isEmpty()&&!base.startsWith("https://"))return;JSONObject clean=new JSONObject();clean.put("base",base);clean.put("remember",obj.optBoolean("remember"));clean.put("token",obj.optBoolean("remember")?obj.optString("token"):"");prefs.edit().putString("studio_settings",clean.toString()).apply();}catch(Exception ignored){}
    }
    @JavascriptInterface public void speak(String text,String language,float rate,boolean export){
      if(!trustedPage)return;
      runOnUiThread(()->{
        if(!ttsReady){voiceError("Telefon ovoz dvigateli hali tayyor emas.");return;}
        if(text==null||text.trim().isEmpty()||text.length()>TextToSpeech.getMaxSpeechInputLength()){voiceError("Matn bo‘sh yoki qurilma ovoz dvigateli uchun uzun.");return;}
        Locale locale=Locale.forLanguageTag(language);int availability=tts.isLanguageAvailable(locale);
        if(availability<0){voiceError("Tanlangan til ovozi telefonda yo‘q. TTS sozlamalaridan ovozni o‘rnat.");return;}
        tts.setLanguage(locale);tts.setSpeechRate(Math.max(.5f,Math.min(1.5f,rate)));String ticket="tts-"+System.currentTimeMillis();
        if(export){File file=new File(getCacheDir(),ticket+".wav");speechFiles.put(ticket,file);if(tts.synthesizeToFile(text,new Bundle(),file,ticket)==TextToSpeech.ERROR){speechFiles.remove(ticket);voiceError("Ovoz faylga saqlanmadi.");}}
        else tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,ticket);
      });
    }
    @JavascriptInterface public void stopSpeech(){runOnUiThread(()->{if(tts!=null)tts.stop();});}
    @JavascriptInterface public synchronized boolean beginDownload(String ticket,String name,String mime,long encodedSize){
      if(!trustedPage||downloadStream!=null||pendingSave!=null||encodedSize<=0||encodedSize>715827884L||!ticket.matches("[a-zA-Z0-9-]+"))return false;
      try{downloadToGallery=false;downloadTicket=ticket;downloadExpected=encodedSize;downloadWritten=0;downloadName=name.replaceAll("[\\\\/:*?\"<>|]","_");if(downloadName.length()>160)downloadName=downloadName.substring(0,160);downloadMime=mime.split(";")[0];downloadFile=new File(getCacheDir(),"download-"+ticket);downloadStream=new FileOutputStream(downloadFile);return true;}catch(Exception e){return false;}
    }
    @JavascriptInterface public synchronized boolean beginGalleryDownload(String ticket,String name,String mime,long encodedSize){
      if(mime==null||(!mime.startsWith("image/")&&!mime.startsWith("video/")))return false;
      if(!beginDownload(ticket,name,mime,encodedSize))return false;
      downloadToGallery=Build.VERSION.SDK_INT>=29;return true;
    }
    @JavascriptInterface public synchronized void downloadChunk(String ticket,String chunk){
      if(!trustedPage||downloadStream==null||!ticket.equals(downloadTicket))return;
      try{downloadWritten+=chunk.length();if(downloadWritten>downloadExpected)throw new IOException();downloadStream.write(android.util.Base64.decode(chunk,android.util.Base64.DEFAULT));}catch(Exception e){try{downloadStream.close();}catch(Exception ignored){}downloadStream=null;downloadFile.delete();downloadMessage("Fayl yozilmadi.");}
    }
    @JavascriptInterface public synchronized void finishDownload(String ticket){
      if(!trustedPage||downloadStream==null||!ticket.equals(downloadTicket))return;
      try{downloadStream.close();downloadStream=null;if(downloadWritten!=downloadExpected)throw new IOException();
        if(downloadToGallery){downloadToGallery=false;saveMediaToGallery(downloadFile,downloadName,downloadMime);return;}
        pendingSave=downloadFile;
        runOnUiThread(()->{Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType(downloadMime.isEmpty()?"application/octet-stream":downloadMime);intent.putExtra(Intent.EXTRA_TITLE,downloadName);try{startActivityForResult(intent,20);}catch(Exception e){pendingSave=null;downloadMessage("Fayl tanlash oynasi ochilmadi.");}});
      }catch(Exception e){downloadMessage("Fayl tugallanmagan.");}
    }
  }
  @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] results){
    super.onRequestPermissionsResult(requestCode,permissions,results);
    if(requestCode==30&&pendingPermission!=null){if(results.length>0&&results[0]==PackageManager.PERMISSION_GRANTED)pendingPermission.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});else pendingPermission.deny();pendingPermission=null;}
  }
  @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
    super.onActivityResult(requestCode,resultCode,data);
    if(requestCode==10&&chooser!=null){ArrayList<Uri> uris=new ArrayList<>();if(resultCode==RESULT_OK&&data!=null){if(data.getClipData()!=null)for(int i=0;i<data.getClipData().getItemCount();i++)uris.add(data.getClipData().getItemAt(i).getUri());else if(data.getData()!=null)uris.add(data.getData());}chooser.onReceiveValue(uris.isEmpty()?null:uris.toArray(new Uri[0]));chooser=null;}
    if(requestCode==20&&pendingSave!=null){final File file=pendingSave;pendingSave=null;if(resultCode!=RESULT_OK||data==null||data.getData()==null){file.delete();return;}final Uri uri=data.getData();new Thread(()->{try(InputStream input=new FileInputStream(file);OutputStream output=getContentResolver().openOutputStream(uri)){if(output==null)throw new IOException();byte[] buffer=new byte[65536];int n;while((n=input.read(buffer))!=-1)output.write(buffer,0,n);downloadMessage("Fayl telefonga saqlandi.");}catch(Exception e){downloadMessage("Faylni saqlab bo‘lmadi.");}finally{file.delete();}}).start();}
  }
  private void notifyExportInterrupted(){if(web!=null&&trustedPage)web.evaluateJavascript("window.onNativeExportInterrupted && window.onNativeExportInterrupted()",null);}
  @Override protected void onPause(){if(exportActive){exportInterrupted=true;notifyExportInterrupted();}super.onPause();}
  @Override protected void onResume(){super.onResume();if(exportInterrupted){exportInterrupted=false;notifyExportInterrupted();}}
  @Override public void onBackPressed(){web.evaluateJavascript("location.hash === '#home' || location.hash === ''",result->{if("true".equals(result))MainActivity.super.onBackPressed();else web.evaluateJavascript("document.querySelector('[data-page=home]').click()",null);});}
  private void serverFailure(String ticket,Exception error){
    String message=error instanceof java.net.SocketTimeoutException?"Server javobi kechikdi. Qayta yuborishdan oldin Galereyadagi ishlarni tekshir.":error instanceof java.net.UnknownHostException?"Server manzili topilmadi. Manzil va internetni tekshir.":error instanceof javax.net.ssl.SSLException?"Serverning xavfsiz ulanishini tekshirib bo‘lmadi. Telefon sanasi va internetni tekshir.":error instanceof IOException?error.getMessage():"Server so‘rovini bajarib bo‘lmadi.";
    try{callback("onNativeServerResult",new JSONObject().put("id",ticket).put("error",message==null?"Serverga ulanib bo‘lmadi.":message));}catch(Exception ignored){}
  }
  @Override protected void onDestroy(){trustedPage=false;for(ServerHttp.Call call:serverCalls.values())call.cancel();serverWorkers.shutdownNow();for(File file:serverMedia.values())file.delete();serverMedia.clear();serverMediaTypes.clear();if(tts!=null){tts.stop();tts.shutdown();}if(chooser!=null)chooser.onReceiveValue(null);if(web!=null)web.destroy();super.onDestroy();}
}
