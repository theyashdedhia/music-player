package Task1;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.File;
import java.util.Iterator;

public class MusicDataLoad {
        public static void main(String[] args) throws Exception {

            AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                    .withCredentials(new ProfileCredentialsProvider())
                    .withRegion(Regions.US_EAST_1)
                    .build();

            DynamoDB dynamoDB = new DynamoDB(client);

            Table table = dynamoDB.getTable("music");

            JsonParser parser = new JsonFactory().createParser(new File("C:\\Users\\Yash\\Desktop\\LearningInPublic\\Sem 3\\Cloud\\music-player\\music-player\\data\\2025a1.json"));

            JsonNode rootNode = new ObjectMapper().readTree(parser);
            Iterator<JsonNode> iteratorForJsonData = rootNode.get("songs").iterator();

            ObjectNode currentNode;

            while (iteratorForJsonData.hasNext()) {
                currentNode = (ObjectNode) iteratorForJsonData.next();

                String title = currentNode.path("title").asText();
                String artist = currentNode.path("artist").asText();
                String year = currentNode.path("year").asText();
                String album = currentNode.path("album").asText();
                String image_url = currentNode.path("img_url").asText();

                try {
                    table.putItem(new Item().withPrimaryKey("year", year, "title", title).withString("artist", artist).withString("album", album).withString("img_url", image_url));
                    System.out.println("PutItem succeeded: " + year + " " + title);

                }
                catch (Exception e) {
                    System.err.println("Unable to add movie: " + year + " " + title);
                    System.err.println(e.getMessage());
                    break;
                }
            }
            parser.close();
        }
}
