package uz.shirin.ai;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import javax.net.ssl.HttpsURLConnection;

/** Authenticated native HTTPS transport for the app's own server API. */
public final class ServerHttp {
  private ServerHttp(){}
  static final int MAX_JSON=32*1024*1024,MAX_UPLOAD=256*1024*1024;
  static final long MAX_MEDIA=512L*1024*1024;
  interface Factory { HttpsURLConnection open(URL url) throws IOException; }
  public static final class Reply {
    public final int status;public final String body;
    Reply(int status,String body){this.status=status;this.body=body;}
  }
  static URI baseUri(String value) throws IOException {
    try {
      URI uri=new URI(value);
      if(!"https".equalsIgnoreCase(uri.getScheme())||uri.getHost()==null||uri.getRawUserInfo()!=null||uri.getRawQuery()!=null||uri.getRawFragment()!=null||!(uri.getRawPath().isEmpty()||"/".equals(uri.getRawPath()))||uri.getPort()==0||uri.getPort()>65535)throw new Exception();
      return new URI("https",null,uri.getHost(),uri.getPort(),"/",null,null);
    }catch(Exception e){throw new IOException("Serverning asosiy HTTPS manzilini tekshir.");}
  }
  static URL apiUrl(String base,String path,boolean post) throws IOException {
    boolean allowed=post?path.matches("/(jobs|image|voice|chat|agent)")||path.matches("/jobs/[A-Za-z0-9_-]{1,100}/cancel"):path.matches("/(health|healthz|models|jobs)")||path.matches("/jobs/[A-Za-z0-9_-]{1,100}");
    if(!allowed)throw new IOException("Server so‘rovi yo‘li noto‘g‘ri.");
    return baseUri(base).resolve(path).toURL();
  }
  static URL mediaUrl(String base,String value) throws IOException {
    try {
      URI origin=baseUri(base),uri=new URI(value);
      int a=origin.getPort()==-1?443:origin.getPort(),b=uri.getPort()==-1?443:uri.getPort();
      if(!"https".equalsIgnoreCase(uri.getScheme())||!origin.getHost().equalsIgnoreCase(uri.getHost())||a!=b||uri.getRawUserInfo()!=null||uri.getRawQuery()!=null||uri.getRawFragment()!=null||!uri.getRawPath().matches("/media/[A-Za-z0-9_./-]+")||uri.getRawPath().contains(".."))throw new Exception();
      return uri.toURL();
    }catch(Exception e){throw new IOException("Media manzili tanlangan serverga mos emas.");}
  }
  public static final class Call {
    private final Factory factory;
    private volatile HttpsURLConnection connection;
    private volatile boolean cancelled;
    public Call(){this(url->(HttpsURLConnection)url.openConnection());}
    Call(Factory factory){this.factory=factory;}
    public void cancel(){cancelled=true;HttpsURLConnection c=connection;if(c!=null)c.disconnect();}
    private void check() throws IOException {if(cancelled)throw new IOException("So‘rov bekor qilindi.");}
    private HttpsURLConnection open(URL url,int timeout) throws IOException {
      check();HttpsURLConnection c=factory.open(url);connection=c;check();
      c.setInstanceFollowRedirects(false);c.setUseCaches(false);
      int limit=Math.max(1000,Math.min(180000,timeout));
      c.setConnectTimeout(Math.min(15000,limit));c.setReadTimeout(limit);
      c.setRequestProperty("Accept-Encoding","identity");
      return c;
    }
    private int status(HttpsURLConnection c) throws IOException {
      check();int code=c.getResponseCode();
      if(code>=300&&code<400)throw new IOException("Server boshqa manzilga yo‘naltirdi. Server manzilini tekshir.");
      return code;
    }
    private long copy(InputStream input,OutputStream output,long limit) throws IOException {
      if(input==null)return 0;byte[] buffer=new byte[65536];long total=0;int n;
      while((n=input.read(buffer))!=-1){check();total+=n;if(total>limit)throw new IOException("Server fayli qurilma uchun juda katta.");output.write(buffer,0,n);}
      check();return total;
    }
    public Reply json(String base,String path,String token,String body,int timeout) throws IOException {
      if(token==null)token="";
      if(token.length()>2048||!token.matches("[\\x20-\\x7E]*"))throw new IOException("Ulanish kodida noto‘g‘ri belgi bor.");
      boolean post=body!=null;URL url=apiUrl(base,path,post);
      if(post&&body.length()>MAX_UPLOAD)throw new IOException("Yuklama juda katta. Rasmlar yoki video hajmini kamaytir.");
      try {
        HttpsURLConnection c=open(url,timeout);c.setRequestMethod(post?"POST":"GET");c.setRequestProperty("Accept","application/json");
        if(!token.isEmpty())c.setRequestProperty("Authorization","Bearer "+token);
        if(post){
          byte[] bytes=body.getBytes(StandardCharsets.UTF_8);
          if(bytes.length>MAX_UPLOAD)throw new IOException("Yuklama juda katta. Rasmlar yoki video hajmini kamaytir.");
          c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json; charset=utf-8");c.setFixedLengthStreamingMode(bytes.length);
          try(OutputStream out=c.getOutputStream()){for(int i=0;i<bytes.length;i+=65536){check();out.write(bytes,i,Math.min(65536,bytes.length-i));}}
        }
        int code=status(c);if(c.getContentLengthLong()>MAX_JSON)throw new IOException("Server javobi juda katta.");
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        try(InputStream in=code>=400?c.getErrorStream():c.getInputStream()){copy(in,out,MAX_JSON);}
        return new Reply(code,new String(out.toByteArray(),StandardCharsets.UTF_8));
      }finally{HttpsURLConnection c=connection;connection=null;if(c!=null)c.disconnect();}
    }
    public String media(String base,String value,File target,int timeout) throws IOException {
      boolean complete=false;
      try {
        HttpsURLConnection c=open(mediaUrl(base,value),timeout);c.setRequestMethod("GET");int code=status(c);
        if(code!=200)throw new IOException("Faylni yuklab bo‘lmadi (HTTP "+code+").");
        String type=c.getContentType();type=type==null?"":type.split(";")[0].trim().toLowerCase(java.util.Locale.ROOT);
        if(!type.matches("(video/(mp4|webm)|image/(png|jpeg|webp)|audio/(mpeg|mp4|wav|x-wav|ogg|webm))"))throw new IOException("Server rasm, video yoki ovoz faylini qaytarmadi.");
        long expected=c.getContentLengthLong();if(expected>MAX_MEDIA)throw new IOException("Server fayli qurilma uchun juda katta.");
        long received;try(InputStream in=c.getInputStream();OutputStream out=new FileOutputStream(target)){received=copy(in,out,MAX_MEDIA);}
        if(received==0||expected>=0&&received!=expected)throw new IOException("Fayl to‘liq yuklanmadi. Qayta urin.");
        complete=true;return type;
      }finally{HttpsURLConnection c=connection;connection=null;if(c!=null)c.disconnect();if(!complete)target.delete();}
    }
  }
}
