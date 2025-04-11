package Task2;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.SdkClientException;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.CreateBucketRequest;
import com.amazonaws.services.s3.model.GetBucketLocationRequest;
import com.amazonaws.services.dynamodbv2.document.spec.ScanSpec;
import com.amazonaws.services.dynamodbv2.document.ItemCollection;
import com.amazonaws.services.dynamodbv2.document.ScanOutcome;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.util.Iterator;

public class ImageS3Load {
    static String BUCKET_NAME = "task2-music-images";
    public static void main(String[] args) throws IOException {
        Regions clientRegion = Regions.US_EAST_1;


        try {
            AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                    .withCredentials(new ProfileCredentialsProvider())
                    .withRegion(clientRegion)
                    .build();

            if (!s3Client.doesBucketExistV2(BUCKET_NAME)) {
                // Because the CreateBucketRequest object doesn't specify a region, the
                // bucket is created in the region specified in the client.
                s3Client.createBucket(new CreateBucketRequest(BUCKET_NAME));

                // Verify that the bucket was created by retrieving it and checking its location.
                String bucketLocation = s3Client.getBucketLocation(new GetBucketLocationRequest(BUCKET_NAME));
                System.out.println("Bucket location: " + bucketLocation);
            } else{
                String bucketLocation = s3Client.getBucketLocation(BUCKET_NAME);
                System.out.println("Bucket location: " + bucketLocation);
            }

            // Connect to Db
            AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                    .withCredentials(new ProfileCredentialsProvider())
                    .withRegion(Regions.US_EAST_1)
                    .build();

            DynamoDB dynamoDB = new DynamoDB(client);
            Table table = dynamoDB.getTable("music");
            // Get the images url data
            ScanSpec scanSpec = new ScanSpec().withProjectionExpression("img_url");
            ItemCollection<ScanOutcome> items = table.scan(scanSpec);
            uploadAllImages(items, s3Client);
            // upload one by one on the bucket
        } catch (AmazonServiceException e) {
            e.printStackTrace();
        } catch (SdkClientException e) {
            e.printStackTrace();
        }
    }

    private static void uploadAllImages(ItemCollection<ScanOutcome> items, AmazonS3 s3Client) {
        try {
            System.out.println("Fetching all img_url from music table...");

            Iterator<Item> iterator = items.iterator();
            while (iterator.hasNext()) {
                Item item = iterator.next();

                //Convert the item to String for downloading
                String imgUrl = item.get("img_url").toString();

                //upload to s3 bucket
                if (imgUrl != null && !imgUrl.isEmpty()) {
                    // Download image as InputStream
                    URL url = new URL(imgUrl);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    InputStream inputStream = connection.getInputStream();
                    // upload the file from input stream to the s3bucket
                    uploadToS3(s3Client, inputStream, connection, imgUrl);
                }
            }
        } catch (Exception e) {
            System.err.println("Error scanning music table: " + e.getMessage());
        }
    }

    private static void uploadToS3(AmazonS3 s3Client, InputStream inputStream, HttpURLConnection connection, String imgUrl) {
        try {
            // Set metadata
            ObjectMetadata metadata = new ObjectMetadata();
            metadata.setContentType("image/jpeg"); // Adjust based on file type
            metadata.setContentLength(connection.getContentLengthLong());

            //extract file name
            String s3Key = "images/" + extractFileName(imgUrl);

            // Upload to S3 directly from InputStream
            s3Client.putObject(new PutObjectRequest(BUCKET_NAME, s3Key, inputStream, metadata));

            System.out.println("Upload successful: " + s3Key);

            // Close InputStream
            inputStream.close();
        } catch (Exception e) {
            System.err.println("Failed to upload to S3: " + e.getMessage());
        }
    }
    public static String extractFileName(String imageUrl) {
        return imageUrl.substring(imageUrl.lastIndexOf("/") + 1);
    }
}
