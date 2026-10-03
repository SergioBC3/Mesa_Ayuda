package co.mesaayuda.insertar;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MongoConfig {

    @Bean(destroyMethod = "close")
    public MongoClient mongoClient(@Value("${MONGODB_URI}") String uri) {
        return MongoClients.create(uri);
    }
}
