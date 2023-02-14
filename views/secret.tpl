<html>
<body>
Enter your secret here...
<form method="post" action="/secret">
  <hr>
  <div>
    <label>Secret</label>
    <input type="text" id="secret" name="secret" value="{{secret}}">
  </div>
  <hr>
  <button type="submit">Submit</button>
</form>
</body>
</html>