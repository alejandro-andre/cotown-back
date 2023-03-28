import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Test {

    // Run
	public static void main(String[] args) throws Exception {
        URL url = new URL("https://dev.cotown.ciber.es/hello");
        InputStreamReader is = new InputStreamReader(url.openStream());
        BufferedReader br = new BufferedReader(is);
        String s;
        while((s = br.readLine()) != null) {
            System.out.println(s);
        }
        br.close();
        is.close();
    }   

}	