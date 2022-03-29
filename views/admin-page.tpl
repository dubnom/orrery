<form method="post">
 {{!form}}
 <button class="doit" name="action" type="submit" value="update">Update</button>
</form>

<div>
 <h4>Tics Discovered</h4>
 <ul>
 %for tic in tics:
  <li>{{!tic}}</li>
 %end
 </ul>
</div>
