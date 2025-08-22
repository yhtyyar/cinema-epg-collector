package com.iptv.movies.data

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory

interface ApiService {
    @GET("api/movies")
    suspend fun listMovies(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("q") query: String? = null,
    ): MoviesResponse

    @GET("api/movies/{id}")
    suspend fun getMovie(@Path("id") id: String): Movie
}

object ApiClient {
    // Эмулятор Android видит локальный хост по адресу 10.0.2.2
    private const val BASE_URL = "http://10.0.2.2:8000/"

    private val httpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
        OkHttpClient.Builder()
            .addInterceptor(logging)
            .build()
    }

    private val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(httpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(ApiService::class.java)
    }

    fun withBaseUrlForPreview(url: String): ApiService {
        return Retrofit.Builder()
            .baseUrl(url)
            .client(httpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(ApiService::class.java)
    }
}

fun buildPosterUrl(raw: String?): String? {
    if (raw.isNullOrBlank()) return null
    return if (raw.startsWith("http")) raw else "http://10.0.2.2:8000" + raw
}
