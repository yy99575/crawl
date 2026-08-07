<template>
  <div class="container">
    <h1>豆瓣电影 Top250</h1>

    <!-- 排序控制区域 -->
    <div class="sort-bar">
      <span>排序方式：</span>
      <select v-model="sortBy">
        <option value="score">按评分</option>
        <option value="rank">按排名</option>
        <option value="score_num">按评价人数</option>
        <option value="release_year">按上映年份</option>
      </select>
      <span class="split">｜</span>
      <span>排列顺序：</span>
      <select v-model="order">
        <option value="asc">升序</option>
        <option value="desc">降序</option>
      </select>
      <button class="search-btn" @click="resetfetchMovies">开始排序</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>排名</th>
          <th>电影名称</th>
          <th>评分</th>
          <th>评价人数</th>
          <th>导演/主演</th>
          <th>类型</th>
          <th>上映年份</th>
         <!--<th>海报</th>--> 
          <th>电影简介</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="movie in movies" :key="movie.rank">
          <td>{{ movie.rank }}</td>
          <td>{{ movie.title }}</td>
          <td>{{ movie.score }}</td>
          <td>{{ movie.score_num }}</td>
          <td>{{ movie.director }}</td>
          <td>{{ movie.type }}</td>
          <td>{{ movie.release_year }}</td>
          <!--<td><img :src="movie.poster_url" :alt="movie.title" width="100"></td>-->
          <td class="desc">{{ movie.introduction }}</td>
        </tr>
      </tbody>
    </table>
    <!--分页功能!-->
    <div class="pagination">
      <button @click="page_del" :disabled="page <= 1">上一页</button>
      <span>第 {{ page }} 页/共 {{ totalPages }} 页</span>
      <button @click="page_add" :disabled="page >= totalPages">下一页</button>
       <input type="number" v-model.number="page" :max="totalPages" :min="1" @change="fetchMovies()" style="width: 60px; margin-left: 10px;" />
    </div>
    <p v-if="loading" class="loading">加载中...</p>
    <p v-else-if="total === 0" class="empty">暂无电影数据，请先运行爬虫</p>
    <p class="total">总共 {{ total }} 条数据</p>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      movies: [],
      total: 0,
      // 排序条件 默认用排名升序
      sortBy: 'rank',
      order: 'asc',
      //页的大小
      page:1,
      page_size:10,
      totalPages: 0,
      loading: false //qing状态，初始为true，表示正在加载数据
    }
  },
  mounted() {
    // 页面初始默认加载排名升序
    this.fetchMovies();
  },
  methods: {
    async fetchMovies() {
        this.loading = true;//请求前打开
      try {
        //多传两个参数 页数和页大小
        const url = `http://localhost:8000/movies?sort_by=${this.sortBy}&order=${this.order}&page=${this.page}&page_size=${this.page_size}`
        console.log('请求地址', url);
        const res = await fetch(url);
        const data = await res.json();
        
        if (data.items) {
          this.movies = data.items;
          this.total = data.total;
          this.page = data.page; // 更新当前页码
          this.page_size = data.page_size; // 更新每页大小
           this.totalPages = Math.ceil(this.total / this.page_size);
        } else if (data.error) {
          console.error('后端出错:', data.error);
  
        }
      } catch (err) {
        console.error('请求失败:', err);
        alert('请求失败，请检查后端服务是否启动');
      }finally {
        this.loading = false; //请求结束关闭
      }
    },
    page_del(){
      if(this.page > 1){
        this.page--;
        this.fetchMovies();
      }
    },
    page_add(){
      if(this.page < this.totalPages){
        this.page++;
        this.fetchMovies();
      }
    },
    resetfetchMovies() {
      this.page = 1; // 重置页码为1
      this.fetchMovies();
    }
  }
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}
.container {
  max-width: 1400px;
  margin: 30px auto;
  padding: 0 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  background-color: #f7f9fc;
  min-height: 100vh;
}

h1 {
  text-align: center;
  color: #2b3253;
  margin-bottom: 24px;
  font-weight: 600;
}

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  font-size: 15px;
}

.sort-bar select {
  padding: 7px 12px;
  border: 1px solid #cbd2e2;
  border-radius: 6px;
  font-size: 14px;
  color: #2b3253;
  outline: none;
  background: #fff;
  transition: border 0.2s;
}

.sort-bar select:focus {
  border-color: #2b3253;
}

.split {
  color: #999;
}

/* 查询按钮 */
.search-btn {
  padding: 7px 20px;
  background-color: #2b3253;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.25s ease;
}

.search-btn:hover {
  background-color: #404a77;
  box-shadow: 0 3px 8px rgba(43, 50, 83, 0.22);
}

.search-btn:active {
  transform: scale(0.97);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

th, td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #e8ecf2;
  font-size: 14px;
  /* 新增下面两行，禁止文字换行 */
  white-space: nowrap;
  overflow: hidden;
}

th {
  background-color: #eef1fa;
  color: #2b3253;
  font-weight: 600;
}

tbody tr:nth-child(even) {
  background-color: #f8f9fd;
}

tbody tr:hover {
  background-color: #e8edfb;
}

/* 简介超出文字省略，防止表格变形 */
.desc {
  max-width: 260px;
  text-align: left;
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

img {
  border-radius: 4px;
  object-fit: cover;
  transition: transform 0.2s;
}
img:hover {
  transform: scale(1.05);
}

.loading {
  text-align: center;
  font-size: 16px;
  color: #666;
  padding: 30px;
}

.total {
  margin-top: 16px;
  text-align: right;
  font-size: 15px;
  color: #555;
}

/* ========== 新增分页样式 ========== */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin: 24px 0;
  font-size: 14px;
}

.pagination button {
  padding: 6px 16px;
  background-color: #2b3253;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background-color: #404a77;
}

.pagination button:disabled {
  background: #b9bcc9;
  cursor: not-allowed;
}

.pagination input {
  padding: 6px;
  border: 1px solid #cbd2e2;
  border-radius: 4px;
  outline: none;
  text-align: center;
}
.pagination input:focus {
  border-color: #2b3253;
}
.empty {
  text-align: center;
  font-size: 29px;
  color: #0c0000;
  padding: 30px;
}
</style>