package Task1;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.*;

import java.util.Arrays;

public class MusicCreateTable {
        public static void main(String[] args) throws Exception {

            AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                    .withCredentials(new ProfileCredentialsProvider())
                    .withRegion(Regions.US_EAST_1)
                    .build();

            DynamoDB dynamoDB = new DynamoDB(client);

            String tableName = "music";

            try {
                System.out.println("Attempting to create table; please wait...");
                 // Year and title are used as Partition key and sort key
                Table table = dynamoDB.createTable(
                        tableName,
                        Arrays.asList(
                                new KeySchemaElement("year", KeyType.HASH),
                                new KeySchemaElement("title", KeyType.RANGE)),
                        Arrays.asList(
                                new AttributeDefinition("year", ScalarAttributeType.S),
                                new AttributeDefinition("title", ScalarAttributeType.S)),
                        new ProvisionedThroughput(10L, 10L)
                );
                table.waitForActive();
                System.out.println("Success.  Table status: " + table.getDescription().getTableStatus());

            } catch (Exception e) {
                System.err.println("Unable to create table: ");
                System.err.println(e.getMessage());
            }

        }
}
