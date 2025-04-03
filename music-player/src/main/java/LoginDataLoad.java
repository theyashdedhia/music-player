import java.io.File;
import java.util.Iterator;

import com.amazonaws.client.builder.AwsClientBuilder;
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
public class LoginDataLoad {
        public static void main(String[] args) throws Exception {

            AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                    .withEndpointConfiguration(
                            new AwsClientBuilder.EndpointConfiguration(
                                    "http://localhost:8000",
                                    Regions.US_EAST_1.getName()))
                    .build();

            DynamoDB dynamoDB = new DynamoDB(client);

            Table table = dynamoDB.getTable("login");

            JsonParser parser = new JsonFactory().createParser(new File("data/loginData.json"));

            JsonNode rootNode = new ObjectMapper().readTree(parser);
            Iterator<JsonNode> iteratorForJsonData = rootNode.iterator();

            ObjectNode currentNode;

            while (iteratorForJsonData.hasNext()) {
                currentNode = (ObjectNode) iteratorForJsonData.next();

                String email = currentNode.path("email").asText();
                String user_name = currentNode.path("user_name").asText();
                String password = currentNode.path("password").asText();

                try {
                    table.putItem(new Item().withPrimaryKey("email", email, "user_name", user_name).withString("password", password));
                    System.out.println("PutItem succeeded: " + email + " " + user_name);

                }
                catch (Exception e) {
                    System.err.println("Unable to add movie: " + email + " " + user_name);
                    System.err.println(e.getMessage());
                    break;
                }
            }
            parser.close();
        }
}
