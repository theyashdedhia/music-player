package Task1;

import java.util.Arrays;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.AttributeDefinition;
import com.amazonaws.services.dynamodbv2.model.KeySchemaElement;
import com.amazonaws.services.dynamodbv2.model.KeyType;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.model.ScalarAttributeType;
public class LoginCreateTable {
        public static void main(String[] args) throws Exception {

            AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                    .withCredentials(new ProfileCredentialsProvider())
                    .withRegion(Regions.US_EAST_1)
                    .build();

            DynamoDB dynamoDB = new DynamoDB(client);

            String tableName = "login";

            try {
                System.out.println("Attempting to create table; please wait...");
                 // Email and user_name are used as Partition key and sort key
                Table table = dynamoDB.createTable(
                    tableName,
                    Arrays.asList(
                        new KeySchemaElement("email", KeyType.HASH),  // Partition Key
                        new KeySchemaElement("user_name", KeyType.RANGE) // Sort Key
                    ),
                    Arrays.asList(
                        new AttributeDefinition("email", ScalarAttributeType.S),
                        new AttributeDefinition("user_name", ScalarAttributeType.S)
                    ),
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
